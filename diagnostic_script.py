#!/usr/bin/env python3
"""
FastAPI App Diagnostic Script
Comprehensive audit of all routes, templates, navigation, and breadcrumbs.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp


class FastAPIDiagnostic:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {"total_routes": 0, "passed": 0, "failed": 0, "errors": []},
            "route_tests": [],
            "navigation_tests": [],
            "breadcrumb_tests": [],
            "template_tests": [],
            "error_cases": [],
        }

    async def test_route(
        self,
        session: aiohttp.ClientSession,
        method: str,
        path: str,
        expected_status: int = 200,
        description: str = "",
    ) -> Dict[str, Any]:
        """Test a single route."""
        url = f"{self.base_url}{path}"
        test_result = {
            "method": method,
            "path": path,
            "url": url,
            "expected_status": expected_status,
            "description": description,
            "status": "unknown",
            "response_status": None,
            "error": None,
            "response_time": None,
        }

        try:
            start_time = time.time()
            # For redirect tests, don't follow redirects to check the actual redirect status
            follow_redirects = expected_status != 302
            async with session.request(
                method, url, allow_redirects=follow_redirects
            ) as response:
                test_result["response_time"] = time.time() - start_time
                test_result["response_status"] = response.status

                if response.status == expected_status:
                    test_result["status"] = "PASS"
                    self.results["summary"]["passed"] += 1
                else:
                    test_result["status"] = "FAIL"
                    test_result["error"] = (
                        f"Expected {expected_status}, got {response.status}"
                    )
                    self.results["summary"]["failed"] += 1

                # Check for template errors in HTML responses
                if response.status == 200 and response.content_type == "text/html":
                    content = await response.text()
                    # Look for actual template errors, not JavaScript error handling
                    if (
                        "jinja2.exceptions" in content.lower()
                        or "template error" in content.lower()
                        or "template exception" in content.lower()
                        or "jinja2 error" in content.lower()
                    ):
                        test_result["status"] = "FAIL"
                        test_result["error"] = "Template error detected in response"
                        self.results["summary"]["failed"] += 1
                        self.results["summary"]["passed"] -= 1

        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
            self.results["summary"]["failed"] += 1

        self.results["route_tests"].append(test_result)
        self.results["summary"]["total_routes"] += 1
        return test_result

    async def test_navigation_flow(self, session: aiohttp.ClientSession) -> None:
        """Test user navigation flows."""
        navigation_tests = [
            {
                "name": "Homepage → New Inspection → Industries",
                "steps": [
                    ("GET", "/", 200, "Homepage"),
                    ("GET", "/inspection/new", 302, "New Inspection (should redirect)"),
                    ("GET", "/industries", 200, "Industries page"),
                ],
            },
            {
                "name": "Inspections List → Inspection Detail",
                "steps": [
                    ("GET", "/inspections", 200, "Inspections list"),
                    (
                        "GET",
                        "/inspection/9999999",
                        404,
                        "Invalid inspection (should 404)",
                    ),
                ],
            },
            {
                "name": "Industry Selection → New Industry Inspection",
                "steps": [
                    ("GET", "/industries", 200, "Industries page"),
                    (
                        "GET",
                        "/industries/automotive/new",
                        200,
                        "Automotive new inspection",
                    ),
                    (
                        "GET",
                        "/industries/invalid/new",
                        404,
                        "Invalid industry (should 404)",
                    ),
                ],
            },
        ]

        for nav_test in navigation_tests:
            nav_result = {"name": nav_test["name"], "steps": [], "status": "PASS"}

            for method, path, expected_status, description in nav_test["steps"]:
                step_result = await self.test_route(
                    session, method, path, expected_status, description
                )
                nav_result["steps"].append(step_result)

                if step_result["status"] != "PASS":
                    nav_result["status"] = "FAIL"

            self.results["navigation_tests"].append(nav_result)

    async def test_breadcrumbs(self, session: aiohttp.ClientSession) -> None:
        """Test breadcrumb functionality."""
        breadcrumb_tests = [
            ("/", "Homepage breadcrumbs"),
            ("/inspections", "Inspections breadcrumbs"),
            ("/industries", "Industries breadcrumbs"),
            ("/industries/automotive/new", "Industry inspection breadcrumbs"),
        ]

        for path, description in breadcrumb_tests:
            breadcrumb_result = {
                "path": path,
                "description": description,
                "status": "unknown",
                "breadcrumbs_found": False,
                "breadcrumb_links": [],
                "error": None,
            }

            try:
                async with session.get(f"{self.base_url}{path}") as response:
                    if response.status == 200:
                        content = await response.text()

                        # Check for breadcrumb elements
                        if "breadcrumb" in content.lower():
                            breadcrumb_result["breadcrumbs_found"] = True

                            # Check for breadcrumb links
                            if "href=" in content and "breadcrumb" in content:
                                breadcrumb_result["breadcrumb_links"] = [
                                    "Breadcrumb links detected"
                                ]
                                breadcrumb_result["status"] = "PASS"
                            else:
                                breadcrumb_result["status"] = "FAIL"
                                breadcrumb_result["error"] = "Breadcrumb links missing"
                        else:
                            breadcrumb_result["status"] = "FAIL"
                            breadcrumb_result["error"] = "No breadcrumbs found"
                    else:
                        breadcrumb_result["status"] = "FAIL"
                        breadcrumb_result["error"] = f"Page returned {response.status}"

            except Exception as e:
                breadcrumb_result["status"] = "ERROR"
                breadcrumb_result["error"] = str(e)

            self.results["breadcrumb_tests"].append(breadcrumb_result)

    async def test_error_cases(self, session: aiohttp.ClientSession) -> None:
        """Test error handling cases."""
        error_tests = [
            ("GET", "/inspection/9999999", 404, "Invalid inspection ID"),
            ("GET", "/industries/invalid/new", 404, "Invalid industry"),
            ("GET", "/nonexistent", 404, "Non-existent route"),
            ("POST", "/api/inspections/9999999", 404, "Invalid API endpoint"),
        ]

        for method, path, expected_status, description in error_tests:
            error_result = await self.test_route(
                session, method, path, expected_status, description
            )
            self.results["error_cases"].append(error_result)

    async def test_api_endpoints(self, session: aiohttp.ClientSession) -> None:
        """Test API endpoints."""
        api_tests = [
            ("GET", "/api/inspections", 200, "List inspections API"),
            ("GET", "/api/inspection-template", 200, "Inspection template API"),
            (
                "GET",
                "/api/industries/automotive/template",
                200,
                "Automotive template API",
            ),
            ("GET", "/vehicle/health", 200, "Vehicle service health"),
            (
                "GET",
                "/invoices/api/invoices",
                404,
                "Invoices API (should 404 without auth)",
            ),
        ]

        for method, path, expected_status, description in api_tests:
            await self.test_route(session, method, path, expected_status, description)

    async def test_templates(self, session: aiohttp.ClientSession) -> None:
        """Test template rendering."""
        template_tests = [
            ("/", "Homepage template"),
            ("/inspections", "Inspections list template"),
            ("/industries", "Industries template"),
            ("/industries/automotive/new", "Automotive inspection template"),
        ]

        for path, description in template_tests:
            template_result = {
                "path": path,
                "description": description,
                "status": "unknown",
                "template_rendered": False,
                "error": None,
            }

            try:
                async with session.get(f"{self.base_url}{path}") as response:
                    if response.status == 200:
                        content = await response.text()

                        # Check for basic HTML structure
                        if "<html" in content and "</html>" in content:
                            template_result["template_rendered"] = True
                            template_result["status"] = "PASS"
                        else:
                            template_result["status"] = "FAIL"
                            template_result["error"] = "Invalid HTML structure"
                    else:
                        template_result["status"] = "FAIL"
                        template_result["error"] = f"Page returned {response.status}"

            except Exception as e:
                template_result["status"] = "ERROR"
                template_result["error"] = str(e)

            self.results["template_tests"].append(template_result)

    async def run_diagnostics(self) -> Dict[str, Any]:
        """Run all diagnostic tests."""
        print("🚀 Starting FastAPI App Diagnostic...")
        print(f"📡 Testing against: {self.base_url}")

        # Check if server is running
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/") as response:
                    if response.status != 200:
                        print("❌ Server not responding properly")
                        return self.results
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return self.results

        print("✅ Server is running, starting tests...")

        async with aiohttp.ClientSession() as session:
            # Test basic routes
            print("\n🔍 Testing basic routes...")
            basic_routes = [
                ("GET", "/", 200, "Homepage"),
                ("GET", "/inspections", 200, "Inspections list"),
                ("GET", "/inspection/new", 302, "New inspection (redirect)"),
                ("GET", "/industries", 200, "Industries page"),
                ("GET", "/invoices", 200, "Invoices page"),
            ]

            for method, path, expected_status, description in basic_routes:
                await self.test_route(
                    session, method, path, expected_status, description
                )

            # Test navigation flows
            print("\n🧭 Testing navigation flows...")
            await self.test_navigation_flow(session)

            # Test breadcrumbs
            print("\n🍞 Testing breadcrumbs...")
            await self.test_breadcrumbs(session)

            # Test error cases
            print("\n⚠️ Testing error cases...")
            await self.test_error_cases(session)

            # Test API endpoints
            print("\n🔌 Testing API endpoints...")
            await self.test_api_endpoints(session)

            # Test templates
            print("\n📄 Testing template rendering...")
            await self.test_templates(session)

        return self.results

    def generate_report(self) -> str:
        """Generate comprehensive diagnostic report."""
        report = []
        report.append("=" * 80)
        report.append("FASTAPI APP DIAGNOSTIC REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {self.results['timestamp']}")
        report.append(f"Base URL: {self.base_url}")
        report.append("")

        # Summary
        summary = self.results["summary"]
        report.append("📊 SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Routes Tested: {summary['total_routes']}")
        report.append(f"✅ Passed: {summary['passed']}")
        report.append(f"❌ Failed: {summary['failed']}")
        report.append(
            f"Success Rate: {(summary['passed'] / summary['total_routes'] * 100):.1f}%"
            if summary["total_routes"] > 0
            else "N/A"
        )
        report.append("")

        # Route Tests
        report.append("🔍 ROUTE TESTS")
        report.append("-" * 40)
        for test in self.results["route_tests"]:
            status_icon = "✅" if test["status"] == "PASS" else "❌"
            report.append(
                f"{status_icon} {test['method']} {test['path']} - {test['description']}"
            )
            if test["error"]:
                report.append(f"   Error: {test['error']}")
        report.append("")

        # Navigation Tests
        report.append("🧭 NAVIGATION TESTS")
        report.append("-" * 40)
        for nav_test in self.results["navigation_tests"]:
            status_icon = "✅" if nav_test["status"] == "PASS" else "❌"
            report.append(f"{status_icon} {nav_test['name']}")
            for step in nav_test["steps"]:
                step_icon = "✅" if step["status"] == "PASS" else "❌"
                report.append(
                    f"   {step_icon} {step['method']} {step['path']} - {step['description']}"
                )
                if step["error"]:
                    report.append(f"      Error: {step['error']}")
        report.append("")

        # Breadcrumb Tests
        report.append("🍞 BREADCRUMB TESTS")
        report.append("-" * 40)
        for breadcrumb_test in self.results["breadcrumb_tests"]:
            status_icon = "✅" if breadcrumb_test["status"] == "PASS" else "❌"
            report.append(
                f"{status_icon} {breadcrumb_test['path']} - {breadcrumb_test['description']}"
            )
            if breadcrumb_test["error"]:
                report.append(f"   Error: {breadcrumb_test['error']}")
        report.append("")

        # Template Tests
        report.append("📄 TEMPLATE TESTS")
        report.append("-" * 40)
        for template_test in self.results["template_tests"]:
            status_icon = "✅" if template_test["status"] == "PASS" else "❌"
            report.append(
                f"{status_icon} {template_test['path']} - {template_test['description']}"
            )
            if template_test["error"]:
                report.append(f"   Error: {template_test['error']}")
        report.append("")

        # Error Cases
        report.append("⚠️ ERROR CASE TESTS")
        report.append("-" * 40)
        for error_test in self.results["error_cases"]:
            status_icon = "✅" if error_test["status"] == "PASS" else "❌"
            report.append(
                f"{status_icon} {error_test['method']} {error_test['path']} - {error_test['description']}"
            )
            if error_test["error"]:
                report.append(f"   Error: {error_test['error']}")
        report.append("")

        # Issues Found
        issues = []
        for test in (
            self.results["route_tests"]
            + self.results["navigation_tests"]
            + self.results["breadcrumb_tests"]
            + self.results["template_tests"]
            + self.results["error_cases"]
        ):
            if test["status"] != "PASS":
                if "route_tests" in str(test):
                    tag = "[ROUTE]"
                elif "navigation_tests" in str(test):
                    tag = "[NAVIGATION]"
                elif "breadcrumb_tests" in str(test):
                    tag = "[BREADCRUMB]"
                elif "template_tests" in str(test):
                    tag = "[TEMPLATE]"
                elif "error_cases" in str(test):
                    tag = "[404]" if "404" in str(test) else "[ERROR]"
                else:
                    tag = "[UNKNOWN]"

                issues.append(
                    {
                        "tag": tag,
                        "route": test.get("path", test.get("url", "Unknown")),
                        "error": test.get("error", "Unknown error"),
                        "suggestion": self._generate_suggestion(test),
                    }
                )

        if issues:
            report.append("🚨 ISSUES FOUND")
            report.append("-" * 40)
            for issue in issues:
                report.append(f"{issue['tag']} {issue['route']}")
                report.append(f"   Error: {issue['error']}")
                report.append(f"   Suggestion: {issue['suggestion']}")
                report.append("")
        else:
            report.append("🎉 NO ISSUES FOUND - All tests passed!")
            report.append("")

        report.append("=" * 80)
        report.append("END OF DIAGNOSTIC REPORT")
        report.append("=" * 80)

        return "\n".join(report)

    def _generate_suggestion(self, test: Dict[str, Any]) -> str:
        """Generate suggestion for fixing an issue."""
        error = test.get("error", "").lower()

        if "404" in error:
            return "Check if route is properly registered in FastAPI app"
        elif "template" in error:
            return "Verify template file exists and has correct syntax"
        elif "breadcrumb" in error:
            return "Ensure breadcrumb component is included in template"
        elif "redirect" in error:
            return "Check redirect logic in route handler"
        elif "500" in error:
            return "Check server logs for internal error details"
        else:
            return "Review route implementation and error handling"


async def main():
    """Main diagnostic function."""
    # Check if server is running
    print("🔍 Checking if FastAPI server is running...")

    try:
        # Try to start server if not running
        import subprocess
        import time

        # Check if port 8000 is in use
        result = subprocess.run(["lsof", "-ti:8000"], capture_output=True, text=True)
        if result.returncode != 0:
            print("🚀 Starting FastAPI server...")
            subprocess.Popen(
                ["python3", "main.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(3)  # Wait for server to start
        else:
            print("✅ Server already running on port 8000")
    except Exception as e:
        print(f"⚠️ Could not check server status: {e}")

    # Run diagnostics
    diagnostic = FastAPIDiagnostic()
    results = await diagnostic.run_diagnostics()

    # Generate report
    report = diagnostic.generate_report()

    # Save report to file
    with open("WE_FIX_WITHOUT_MAKING_ANY_CHANGES_UNTIL_I_APPROVE_THEM.txt", "w") as f:
        f.write(report)

    print("\n" + "=" * 80)
    print("📋 DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print(
        f"✅ Report saved to: WE_FIX_WITHOUT_MAKING_ANY_CHANGES_UNTIL_I_APPROVE_THEM.txt"
    )
    print(
        f"📊 Summary: {results['summary']['passed']}/{results['summary']['total_routes']} tests passed"
    )
    print("=" * 80)

    # Print summary to console
    print("\n" + report)


if __name__ == "__main__":
    asyncio.run(main())
