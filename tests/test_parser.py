"""
tests/test_parser.py
====================
TDD test suite for Team Member 1 components:

    compiler/ir.py           – WorkflowIR & StepNode models
    compiler/ambiguity.py    – Semantic Ambiguity Firewall
    compiler/parser.py       – LLM parser + offline fallback
    compiler/authorization.py – RBAC matrix

Running tests
-------------
    # From project root (offline – no API key required):
    OFFLINE_MODE=True pytest tests/test_parser.py -v

    # With Gemini API (requires GEMINI_API_KEY env-var):
    pytest tests/test_parser.py -v -m "not offline"

TDD Philosophy applied here
-----------------------------
Each test class is written to SPECIFY behaviour BEFORE (or alongside)
implementation.  Tests are grouped by the module under test and ordered
from simplest contract (data shape) to most complex (integration flow).
"""

from __future__ import annotations

import json
import os
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _force_offline(monkeypatch):
    """Force OFFLINE_MODE so no real API calls are made in CI / unit tests."""
    monkeypatch.setenv("OFFLINE_MODE", "true")


# ===========================================================================
# 1. compiler/ir.py  –  WorkflowIR & StepNode
# ===========================================================================


class TestStepNode:
    """TDD specs for the StepNode Pydantic model."""

    def test_minimal_construction(self):
        """SPEC: StepNode must be creatable with only id, action, role."""
        from compiler.ir import StepNode

        # ARRANGE + ACT
        step = StepNode(id="step_1", action="submit_form", role="Employee")

        # ASSERT – defaults
        assert step.id == "step_1"
        assert step.action == "submit_form"
        assert step.role == "Employee"
        assert step.condition is None
        assert step.is_required is True
        assert step.dependencies == []

    def test_full_construction(self):
        """SPEC: StepNode accepts all optional fields when provided."""
        from compiler.ir import StepNode

        step = StepNode(
            id="step_2",
            action="approve_budget",
            role="Manager",
            condition="amount <= 20000",
            is_required=True,
            dependencies=["step_1"],
        )

        assert step.condition == "amount <= 20000"
        assert step.dependencies == ["step_1"]

    def test_is_required_defaults_true(self):
        """SPEC: is_required must default to True (mandatory step)."""
        from compiler.ir import StepNode

        step = StepNode(id="s", action="a", role="r")
        assert step.is_required is True

    def test_optional_step_creation(self):
        """SPEC: Steps can be optional (is_required=False)."""
        from compiler.ir import StepNode

        step = StepNode(id="s", action="a", role="r", is_required=False)
        assert step.is_required is False

    def test_invalid_missing_required_fields_raises(self):
        """SPEC: Omitting id/action/role must raise a ValidationError."""
        from pydantic import ValidationError
        from compiler.ir import StepNode

        with pytest.raises(ValidationError):
            StepNode(action="submit_form", role="Employee")  # missing id


class TestWorkflowIR:
    """TDD specs for the WorkflowIR Pydantic model."""

    @pytest.fixture
    def sample_ir(self):
        from compiler.ir import StepNode, WorkflowIR

        return WorkflowIR(
            workflow_id="wf-test-001",
            title="Test Workflow",
            trigger="Test event triggered",
            steps=[
                StepNode(id="step_1", action="submit", role="Employee"),
                StepNode(
                    id="step_2",
                    action="approve_budget",
                    role="Manager",
                    condition="amount <= 20000",
                    dependencies=["step_1"],
                ),
            ],
            roles_allowed=["Employee", "Manager"],
        )

    def test_construction(self, sample_ir):
        """SPEC: WorkflowIR construction populates all fields correctly."""
        assert sample_ir.workflow_id == "wf-test-001"
        assert sample_ir.title == "Test Workflow"
        assert len(sample_ir.steps) == 2

    def test_to_dict_returns_dict(self, sample_ir):
        """SPEC: to_dict() must return a plain Python dict."""
        result = sample_ir.to_dict()
        assert isinstance(result, dict)
        assert result["workflow_id"] == "wf-test-001"
        assert isinstance(result["steps"], list)

    def test_to_json_returns_valid_json(self, sample_ir):
        """SPEC: to_json() must return a valid JSON string."""
        json_str = sample_ir.to_json()
        parsed = json.loads(json_str)  # must not raise
        assert parsed["title"] == "Test Workflow"

    def test_from_dict_round_trip(self, sample_ir):
        """SPEC: from_dict(to_dict()) must produce an equivalent object."""
        from compiler.ir import WorkflowIR

        restored = WorkflowIR.from_dict(sample_ir.to_dict())
        assert restored.workflow_id == sample_ir.workflow_id
        assert len(restored.steps) == len(sample_ir.steps)

    def test_from_json_round_trip(self, sample_ir):
        """SPEC: from_json(to_json()) must produce an equivalent object."""
        from compiler.ir import WorkflowIR

        restored = WorkflowIR.from_json(sample_ir.to_json())
        assert restored.title == sample_ir.title

    def test_get_step_existing(self, sample_ir):
        """SPEC: get_step returns the correct StepNode for a valid id."""
        step = sample_ir.get_step("step_1")
        assert step is not None
        assert step.action == "submit"

    def test_get_step_missing_returns_none(self, sample_ir):
        """SPEC: get_step returns None for an unknown id."""
        assert sample_ir.get_step("nonexistent") is None

    def test_required_steps_filters_correctly(self):
        """SPEC: required_steps() returns only steps with is_required=True."""
        from compiler.ir import StepNode, WorkflowIR

        ir = WorkflowIR(
            workflow_id="wf-x",
            title="X",
            trigger="x",
            steps=[
                StepNode(id="s1", action="a1", role="Employee", is_required=True),
                StepNode(id="s2", action="a2", role="Manager", is_required=False),
                StepNode(id="s3", action="a3", role="Admin", is_required=True),
            ],
        )
        required = ir.required_steps()
        assert len(required) == 2
        assert all(s.is_required for s in required)

    def test_roles_in_workflow_distinct(self):
        """SPEC: roles_in_workflow() returns unique roles across all steps."""
        from compiler.ir import StepNode, WorkflowIR

        ir = WorkflowIR(
            workflow_id="wf-y",
            title="Y",
            trigger="y",
            steps=[
                StepNode(id="s1", action="a", role="Employee"),
                StepNode(id="s2", action="b", role="Employee"),
                StepNode(id="s3", action="c", role="Manager"),
            ],
        )
        roles = ir.roles_in_workflow()
        assert sorted(roles) == ["Employee", "Manager"]

    def test_roles_allowed_defaults_to_empty_list(self):
        """SPEC: roles_allowed defaults to [] when not provided."""
        from compiler.ir import StepNode, WorkflowIR

        ir = WorkflowIR(
            workflow_id="wf-z",
            title="Z",
            trigger="z",
            steps=[StepNode(id="s1", action="a", role="Employee")],
        )
        assert ir.roles_allowed == []


# ===========================================================================
# 2. compiler/ambiguity.py  –  Semantic Ambiguity Firewall
# ===========================================================================


class TestAmbiguityFirewall:
    """TDD specs for check_ambiguity()."""

    def test_clean_policy_is_not_ambiguous(self):
        """SPEC: A precise policy with thresholds must return is_ambiguous=False."""
        from compiler.ambiguity import check_ambiguity

        policy = (
            "All vendor invoices exceeding ₹20,000 must be approved by the "
            "Finance Director within 2 business days."
        )
        result = check_ambiguity(policy)

        assert result["is_ambiguous"] is False
        assert result["detected_terms"] == []
        assert result["warnings"] == []
        assert result["suggested_fixes"] == []

    def test_returns_correct_keys(self):
        """SPEC: Return dict must have exactly the four contract keys."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("Submit invoice soon.")
        assert set(result.keys()) == {
            "is_ambiguous",
            "detected_terms",
            "warnings",
            "suggested_fixes",
        }

    def test_detects_soon(self):
        """SPEC: The word 'soon' must be flagged."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("Please process the refund soon.")
        assert result["is_ambiguous"] is True
        assert "soon" in result["detected_terms"]

    def test_detects_urgent(self):
        """SPEC: The word 'urgent' must be flagged."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("This is urgent and must be handled quickly.")
        assert result["is_ambiguous"] is True
        assert "urgent" in result["detected_terms"]
        assert "quick/quickly" in result["detected_terms"]

    def test_detects_large(self):
        """SPEC: The word 'large' must be flagged as unquantified."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("Large purchases require manager sign-off.")
        assert result["is_ambiguous"] is True
        assert "large" in result["detected_terms"]

    def test_detects_senior(self):
        """SPEC: The word 'senior' must be flagged (vague role reference)."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("A senior employee must verify the vendor.")
        assert result["is_ambiguous"] is True
        assert "senior" in result["detected_terms"]

    def test_detects_expensive(self):
        """SPEC: The word 'expensive' must be flagged."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("Expensive items need Finance Director approval.")
        assert result["is_ambiguous"] is True
        assert "expensive" in result["detected_terms"]

    def test_detects_appropriate(self):
        """SPEC: The word 'appropriate' must be flagged."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("Take appropriate action on the request.")
        assert result["is_ambiguous"] is True
        assert "appropriate" in result["detected_terms"]

    def test_missing_currency_threshold_flagged(self):
        """SPEC: Mentioning 'budget' without a currency value must be flagged."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity(
            "Purchases above the approved budget require manager sign-off."
        )
        assert result["is_ambiguous"] is True
        assert "missing_currency_threshold" in result["detected_terms"]

    def test_currency_present_no_threshold_flag(self):
        """SPEC: 'budget' + explicit ₹ amount must NOT trigger threshold flag."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity(
            "Purchases above the approved budget of ₹50,000 require sign-off."
        )
        assert "missing_currency_threshold" not in result["detected_terms"]

    def test_suggested_fixes_parallel_to_detected_terms(self):
        """SPEC: len(suggested_fixes) == len(detected_terms)."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("Handle this urgent request soon.")
        assert len(result["suggested_fixes"]) == len(result["detected_terms"])

    def test_warnings_parallel_to_detected_terms(self):
        """SPEC: len(warnings) == len(detected_terms)."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("Large purchases should be handled soon.")
        assert len(result["warnings"]) == len(result["detected_terms"])

    def test_case_insensitive_detection(self):
        """SPEC: Detection must be case-insensitive (URGENT == urgent)."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("This is URGENT and needs LARGE resources.")
        assert "urgent" in result["detected_terms"]
        assert "large" in result["detected_terms"]

    def test_empty_string_not_ambiguous(self):
        """SPEC: Empty input returns is_ambiguous=False with empty lists."""
        from compiler.ambiguity import check_ambiguity

        result = check_ambiguity("")
        assert result["is_ambiguous"] is False
        assert result["detected_terms"] == []


# ===========================================================================
# 3. compiler/parser.py  –  parse_policy (offline mode)
# ===========================================================================


@pytest.mark.offline
class TestParsePolicy:
    """TDD specs for parse_policy() executed in offline mode.

    These tests NEVER call the Gemini API.  They validate:
    • The returned object is a WorkflowIR
    • Offline fixture selection logic
    • Fallback robustness
    """

    def test_returns_workflow_ir(self, monkeypatch):
        """SPEC: parse_policy must always return a WorkflowIR."""
        from compiler.ir import WorkflowIR
        from compiler.parser import parse_policy

        _force_offline(monkeypatch)
        result = parse_policy("Vendor invoices above ₹20,000 need Finance Director approval.")
        assert isinstance(result, WorkflowIR)

    def test_vendor_policy_loads_vendor_fixture(self, monkeypatch):
        """SPEC: A vendor-related policy should load vendor_payment fixture."""
        from compiler.parser import parse_policy

        _force_offline(monkeypatch)
        result = parse_policy("The vendor invoice must be verified by an employee.")
        assert len(result.steps) > 0
        # Vendor fixture has verify_vendor action
        actions = [s.action for s in result.steps]
        assert any("vendor" in a for a in actions)

    def test_invoice_keyword_loads_vendor_fixture(self, monkeypatch):
        """SPEC: 'invoice' keyword in policy text routes to vendor fixture."""
        from compiler.parser import parse_policy

        _force_offline(monkeypatch)
        result = parse_policy("Submit the invoice for processing.")
        assert result.workflow_id.startswith("wf-vendor")

    def test_payment_keyword_loads_vendor_fixture(self, monkeypatch):
        """SPEC: 'payment' keyword in policy text routes to vendor fixture."""
        from compiler.parser import parse_policy

        _force_offline(monkeypatch)
        result = parse_policy("Process the payment after approval.")
        assert result.workflow_id.startswith("wf-vendor")

    def test_offline_result_has_unique_workflow_id(self, monkeypatch):
        """SPEC: Each offline call must return a unique workflow_id."""
        from compiler.parser import parse_policy

        _force_offline(monkeypatch)
        r1 = parse_policy("Vendor payment policy.")
        r2 = parse_policy("Vendor payment policy.")
        assert r1.workflow_id != r2.workflow_id

    def test_generic_policy_loads_generic_fixture(self, monkeypatch):
        """SPEC: Non-vendor policy text should load the generic fixture."""
        from compiler.parser import parse_policy

        _force_offline(monkeypatch)
        result = parse_policy("All leave requests must be approved by the manager.")
        assert isinstance(result.steps, list)
        assert len(result.steps) > 0

    def test_all_steps_have_required_fields(self, monkeypatch):
        """SPEC: Every StepNode in the result must have id, action, role."""
        from compiler.parser import parse_policy

        _force_offline(monkeypatch)
        result = parse_policy("Vendor invoice for ₹15,000 submitted.")
        for step in result.steps:
            assert step.id
            assert step.action
            assert step.role

    def test_roles_allowed_is_list(self, monkeypatch):
        """SPEC: roles_allowed on the result must be a list (possibly empty)."""
        from compiler.parser import parse_policy

        _force_offline(monkeypatch)
        result = parse_policy("Process refund for customer.")
        assert isinstance(result.roles_allowed, list)

    def test_api_error_triggers_offline_fallback(self, monkeypatch):
        """SPEC: If Gemini API raises, parse_policy falls back gracefully."""
        from compiler.ir import WorkflowIR
        import compiler.parser as parser_mod

        # Simulate live mode but with a broken API call
        monkeypatch.delenv("OFFLINE_MODE", raising=False)
        monkeypatch.setenv("OFFLINE_MODE", "false")

        def _broken_gemini(_text):
            raise ConnectionError("Simulated network failure")

        monkeypatch.setattr(parser_mod, "_call_gemini", _broken_gemini)

        result = parser_mod.parse_policy("Vendor payment request for ₹5,000.")
        assert isinstance(result, WorkflowIR)  # fallback must return IR, not raise


# ===========================================================================
# 4. compiler/authorization.py  –  RBAC Matrix
# ===========================================================================


class TestRolePermissions:
    """TDD specs for ROLE_PERMISSIONS and check_role_permission()."""

    def test_role_permissions_has_all_roles(self):
        """SPEC: ROLE_PERMISSIONS must contain Employee, Manager, Finance_Director, Admin."""
        from compiler.authorization import ROLE_PERMISSIONS

        assert "Employee" in ROLE_PERMISSIONS
        assert "Manager" in ROLE_PERMISSIONS
        assert "Finance_Director" in ROLE_PERMISSIONS
        assert "Admin" in ROLE_PERMISSIONS

    def test_employee_can_submit(self):
        """SPEC: Employee role must be able to 'submit'."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Employee", "submit") is True

    def test_employee_can_verify_vendor(self):
        """SPEC: Employee role must be able to 'verify_vendor'."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Employee", "verify_vendor") is True

    def test_employee_cannot_approve_budget(self):
        """SPEC: Employee must NOT be able to 'approve_budget'."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Employee", "approve_budget") is False

    def test_manager_can_approve_budget_within_limit(self):
        """SPEC: Manager can approve_budget for amount <= 20,000."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Manager", "approve_budget", amount=15_000) is True
        assert check_role_permission("Manager", "approve_budget", amount=20_000) is True

    def test_manager_cannot_approve_budget_above_limit(self):
        """SPEC: Manager CANNOT approve_budget for amount > 20,000."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Manager", "approve_budget", amount=25_000) is False

    def test_finance_director_can_approve_any_amount(self):
        """SPEC: Finance_Director can approve_budget regardless of amount."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Finance_Director", "approve_budget", amount=1_000_000) is True

    def test_finance_director_can_finance_approval(self):
        """SPEC: Finance_Director can perform 'finance_approval'."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Finance_Director", "finance_approval") is True

    def test_finance_director_can_release_payment(self):
        """SPEC: Finance_Director can 'release_payment'."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Finance_Director", "release_payment") is True

    def test_admin_wildcard_allows_any_action(self):
        """SPEC: Admin must be permitted to perform any action (wildcard)."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Admin", "approve_budget") is True
        assert check_role_permission("Admin", "finance_approval") is True
        assert check_role_permission("Admin", "release_payment") is True
        assert check_role_permission("Admin", "some_arbitrary_action") is True

    def test_unknown_role_returns_false(self):
        """SPEC: An unrecognised role must always return False."""
        from compiler.authorization import check_role_permission

        assert check_role_permission("Intern", "submit") is False
        assert check_role_permission("", "submit") is False

    def test_get_role_actions_returns_list(self):
        """SPEC: get_role_actions() must return a list for any valid role."""
        from compiler.authorization import get_role_actions

        assert isinstance(get_role_actions("Employee"), list)
        assert isinstance(get_role_actions("Admin"), list)

    def test_get_role_actions_unknown_role_returns_empty(self):
        """SPEC: get_role_actions() for an unknown role must return []."""
        from compiler.authorization import get_role_actions

        assert get_role_actions("Ghost") == []

    def test_admin_actions_is_wildcard(self):
        """SPEC: Admin actions list must be ['*']."""
        from compiler.authorization import get_role_actions

        assert get_role_actions("Admin") == ["*"]

    def test_list_roles_returns_all_four(self):
        """SPEC: list_roles() must include all four defined roles."""
        from compiler.authorization import list_roles

        roles = list_roles()
        assert "Employee" in roles
        assert "Manager" in roles
        assert "Finance_Director" in roles
        assert "Admin" in roles

    def test_roles_for_action_finance_approval(self):
        """SPEC: roles_for_action('finance_approval') must include Finance_Director and Admin."""
        from compiler.authorization import roles_for_action

        roles = roles_for_action("finance_approval")
        assert "Finance_Director" in roles
        assert "Admin" in roles

    def test_roles_for_action_submit(self):
        """SPEC: roles_for_action('submit') must include Employee and Admin."""
        from compiler.authorization import roles_for_action

        roles = roles_for_action("submit")
        assert "Employee" in roles
        assert "Admin" in roles


# ===========================================================================
# 5. Integration  –  Parse → Ambiguity check pipeline
# ===========================================================================


@pytest.mark.integration
class TestParseAmbiguityIntegration:
    """End-to-end pipeline: parse_policy then check_ambiguity on the title."""

    def test_clean_policy_pipeline(self, monkeypatch):
        """SPEC: A quantified policy parses to IR and passes ambiguity check."""
        from compiler.parser import parse_policy
        from compiler.ambiguity import check_ambiguity

        _force_offline(monkeypatch)
        policy = (
            "Vendor invoices exceeding ₹20,000 must be approved by the "
            "Finance Director within 3 business days."
        )
        ir = parse_policy(policy)
        ambiguity = check_ambiguity(policy)

        assert ir is not None
        assert ambiguity["is_ambiguous"] is False

    def test_vague_policy_pipeline(self, monkeypatch):
        """SPEC: A vague policy parses to IR but fails ambiguity check."""
        from compiler.parser import parse_policy
        from compiler.ambiguity import check_ambiguity

        _force_offline(monkeypatch)
        policy = "Large vendor payments need urgent approval from senior staff."
        ir = parse_policy(policy)
        ambiguity = check_ambiguity(policy)

        assert ir is not None
        assert ambiguity["is_ambiguous"] is True
        assert len(ambiguity["detected_terms"]) >= 3  # large, urgent, senior, staff

    def test_ir_serialisation_in_pipeline(self, monkeypatch):
        """SPEC: Parsed IR can be serialised to JSON and restored without loss."""
        from compiler.ir import WorkflowIR
        from compiler.parser import parse_policy

        _force_offline(monkeypatch)
        ir = parse_policy("Submit vendor invoice for payment processing.")
        json_str = ir.to_json()
        restored = WorkflowIR.from_json(json_str)

        assert restored.workflow_id == ir.workflow_id
        assert len(restored.steps) == len(ir.steps)
