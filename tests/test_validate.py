import sys
import pathlib

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "build"))

import validate as validate_module  # noqa: E402


def test_valid_fixture_passes(valid_fixture_dir):
    errors, tool_count, category_count = validate_module.validate(
        valid_fixture_dir / "categories.yml", valid_fixture_dir / "tools"
    )
    assert errors == []
    assert tool_count == 6
    assert category_count == 2


def test_below_minimum_and_vendor_capture_both_reported(workspace, tool_factory):
    # A category below its minimum used to skip the vendor-concentration
    # check entirely (it lived in the min-entries check's `else` branch), so
    # a contributor fixing the count would only then discover a second,
    # previously-invisible error. Both must be reported in one pass.
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", source_code_url="https://github.com/acme/a"),
            tool_factory(name="B", website_url="https://b.example", source_code_url="https://github.com/acme/b"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("needs at least 3" in e for e in errors)
    assert any("50%" in e and "acme" in e for e in errors)
    assert len(errors) == 2


def test_category_below_minimum_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example"),
            tool_factory(name="B", website_url="https://b.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("needs at least 3" in e for e in errors)


def test_duplicate_url_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://same.example"),
            tool_factory(name="B", website_url="https://same.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("duplicate website_url" in e for e in errors)


def test_duplicate_source_code_url_with_different_names_fails(workspace, tool_factory):
    # CLOSE3-5: two entries with different names and different website_urls
    # but the same source_code_url used to pass validate.py cleanly, and
    # each independently files its own "Remove: <name>" issue on the same
    # 404'd repo — two issues for one dead link. Catching the duplicate here
    # removes the entry-level cause rather than papering over it in the
    # issue-filing title.
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", source_code_url="https://github.com/acme/same-repo"),
            tool_factory(name="B", website_url="https://b.example", source_code_url="https://github.com/acme/same-repo"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("duplicate source_code_url" in e for e in errors)


def test_duplicate_name_with_different_urls_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="Clay", website_url="https://clay.com"),
            tool_factory(name="clay", website_url="https://clay-other.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("duplicate name" in e for e in errors)


def test_missing_period_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", description="No period here"),
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("must end with a period" in e for e in errors)


def test_lowercase_start_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", description="lowercase start."),
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("uppercase" in e for e in errors)


def test_en_dash_in_description_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(
                name="A",
                website_url="https://a.example",
                description="Enrichment – with an en dash.",
            ),
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("en dash" in e for e in errors)


def test_vendor_capture_disclosure_flag_alone_does_not_trigger(workspace, tool_factory):
    # submitted_by_vendor is a disclosure field, not the input to the 50%
    # rule — three different vendors, all self-disclosed, must not trip it.
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", submitted_by_vendor=True),
            tool_factory(name="B", website_url="https://b.example", submitted_by_vendor=True),
            tool_factory(name="C", website_url="https://c.example", submitted_by_vendor=True),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert not any("50%" in e for e in errors)


def test_vendor_capture_4_of_4_one_github_owner_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", source_code_url="https://github.com/acme/a"),
            tool_factory(name="B", website_url="https://b.example", source_code_url="https://github.com/acme/b"),
            tool_factory(name="C", website_url="https://c.example", source_code_url="https://github.com/acme/c"),
            tool_factory(name="D", website_url="https://d.example", source_code_url="https://github.com/acme/d"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("50%" in e and "acme" in e for e in errors)


def test_vendor_capture_2_of_5_passes(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", source_code_url="https://github.com/acme/a"),
            tool_factory(name="B", website_url="https://b.example", source_code_url="https://github.com/acme/b"),
            tool_factory(name="C", website_url="https://c.example"),
            tool_factory(name="D", website_url="https://d.example"),
            tool_factory(name="E", website_url="https://e.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert not any("50%" in e for e in errors)


def test_vendor_capture_3_of_5_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", source_code_url="https://github.com/acme/a"),
            tool_factory(name="B", website_url="https://b.example", source_code_url="https://github.com/acme/b"),
            tool_factory(name="C", website_url="https://c.example", source_code_url="https://github.com/acme/c"),
            tool_factory(name="D", website_url="https://d.example"),
            tool_factory(name="E", website_url="https://e.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("50%" in e and "acme" in e for e in errors)


def test_vendor_capture_exactly_50_percent_fails(workspace, tool_factory):
    # 4 of 8 is exactly half the category. The rule exists to catch a
    # monoculture, and a category that is precisely one vendor's half is the
    # case it was written to prevent — see docs/curation-policy.md #2.
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", source_code_url="https://github.com/acme/a"),
            tool_factory(name="B", website_url="https://b.example", source_code_url="https://github.com/acme/b"),
            tool_factory(name="C", website_url="https://c.example", source_code_url="https://github.com/acme/c"),
            tool_factory(name="D", website_url="https://d.example", source_code_url="https://github.com/acme/d"),
            tool_factory(name="E", website_url="https://e.example"),
            tool_factory(name="F", website_url="https://f.example"),
            tool_factory(name="G", website_url="https://g.example"),
            tool_factory(name="H", website_url="https://h.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("50%" in e and "acme" in e for e in errors)


def test_vendor_key_recognizes_same_vendor_across_url_shapes():
    github_entry = {"source_code_url": "https://github.com/acme/x", "website_url": "https://x.example"}
    website_entry = {"source_code_url": None, "website_url": "https://acme.com"}
    assert validate_module.vendor_key(github_entry, "a") == validate_module.vendor_key(website_entry, "b")


def test_vendor_key_no_url_does_not_cluster():
    entry_a = {"source_code_url": None, "website_url": "https://"}
    entry_b = {"source_code_url": None, "website_url": "https://"}
    assert validate_module.vendor_key(entry_a, "a") != validate_module.vendor_key(entry_b, "b")


# CLOSE3-2: vendor_key's three failure modes.

DIVERGENT_LIVE_ENTRIES = [
    "exa.yml", "make.yml", "n8n.yml", "postmark.yml",
    "sqlmesh.yml", "twenty.yml", "woodpecker.yml",
]


def test_seven_divergent_live_entries_resolve_to_one_vendor_identity():
    # These seven entries in data/tools/ have a source_code_url and a
    # website_url that resolve to two different vendor identities under the
    # naive heuristic (github owner vs. website SLD) — same company, split
    # across two keys, which is exactly what evades the 50% rule when a
    # second entry from the same vendor only carries one of the two URLs.
    root = pathlib.Path(__file__).resolve().parent.parent / "data" / "tools"
    for filename in DIVERGENT_LIVE_ENTRIES:
        tool = yaml.safe_load((root / filename).read_text())
        source_only = {"source_code_url": tool.get("source_code_url"), "website_url": None, "vendor": tool.get("vendor")}
        website_only = {"source_code_url": None, "website_url": tool.get("website_url"), "vendor": tool.get("vendor")}
        key_from_source = validate_module.vendor_key(source_only, filename)
        key_from_website = validate_module.vendor_key(website_only, filename)
        assert key_from_source == key_from_website, (
            f"{filename}: source_code_url resolves to {key_from_source!r}, "
            f"website_url resolves to {key_from_website!r}"
        )


def test_three_unrelated_gitlab_projects_do_not_error(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", source_code_url="https://gitlab.com/one/a"),
            tool_factory(name="B", website_url="https://b.example", source_code_url="https://gitlab.com/two/b"),
            tool_factory(name="C", website_url="https://c.example", source_code_url="https://gitlab.com/three/c"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert not any("50%" in e for e in errors)


def test_three_unrelated_readthedocs_projects_do_not_error(workspace, tool_factory):
    # No source_code_url, so vendor_key must fall through to website_url —
    # a readthedocs.io subdomain must give NO vendor signal rather than
    # being treated as the registrable domain, or three unrelated projects
    # that all happen to host their docs on readthedocs collapse into one
    # "vendor" and trip a false 50% error.
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://one.readthedocs.io/", source_code_url=None),
            tool_factory(name="B", website_url="https://two.readthedocs.io/", source_code_url=None),
            tool_factory(name="C", website_url="https://three.readthedocs.io/", source_code_url=None),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert not any("50%" in e for e in errors)


def test_same_vendor_split_across_github_and_own_domain_errors(workspace, tool_factory):
    # Three entries from one vendor, only reachable if source_code_url and
    # website_url are both resolved and treated as the same identity.
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://acme.com", source_code_url="https://github.com/acme/a"),
            tool_factory(name="B", website_url="https://acme.com", source_code_url=None),
            tool_factory(name="C", website_url="https://other.example", source_code_url=None),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("50%" in e and "acme" in e for e in errors)


def test_multi_part_tlds_do_not_collapse():
    co_uk = validate_module.vendor_key({"source_code_url": None, "website_url": "https://acme.co.uk"}, "a")
    com_au = validate_module.vendor_key({"source_code_url": None, "website_url": "https://acme.com.au"}, "b")
    unrelated_co = validate_module.vendor_key({"source_code_url": None, "website_url": "https://unrelated.co"}, "c")
    assert co_uk != com_au
    assert co_uk != unrelated_co
    assert com_au != unrelated_co


def test_unknown_category_fails(workspace, tool_factory):
    categories_file, tools_dir = workspace(
        tools=[
            tool_factory(name="A", website_url="https://a.example", categories=["Nonexistent"]),
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert any("unknown category" in e for e in errors)


def test_schema_violation_fails(workspace, tool_factory):
    bad = tool_factory(name="A", website_url="https://a.example")
    del bad["has_api"]
    categories_file, tools_dir = workspace(
        tools=[
            bad,
            tool_factory(name="B", website_url="https://b.example"),
            tool_factory(name="C", website_url="https://c.example"),
        ]
    )
    errors, _, _ = validate_module.validate(categories_file, tools_dir)
    assert len(errors) >= 1
