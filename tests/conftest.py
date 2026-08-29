import pathlib
import shutil

import pytest

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

VALID_TOOL = {
    "name": "Clay",
    "website_url": "https://clay.com",
    "description": "Enrichment waterfalls and list building with a spreadsheet interface.",
    "categories": ["Enrichment & Data"],
    "pricing_model": "commercial",
    "source_code_url": None,
    "license": None,
    "has_api": True,
    "has_mcp_server": False,
    "has_cli": False,
    "self_hostable": False,
}

MINIMAL_CATEGORIES = [
    {"slug": "enrichment-data", "name": "Enrichment & Data", "min_entries": 3},
]


@pytest.fixture
def valid_fixture_dir():
    """The committed 6-entry, 2-category valid fixture set."""
    return FIXTURES / "valid"


@pytest.fixture
def tool_factory():
    def make(**overrides):
        return {**VALID_TOOL, **overrides}

    return make


@pytest.fixture
def workspace(tmp_path, tool_factory):
    """A scratch data/ dir with one category (min 3) the test populates."""
    import yaml

    def setup(categories=None, tools=None):
        categories = categories if categories is not None else MINIMAL_CATEGORIES
        tools = tools or []

        data_dir = tmp_path / "data"
        tools_dir = data_dir / "tools"
        tools_dir.mkdir(parents=True)

        categories_file = data_dir / "categories.yml"
        categories_file.write_text(yaml.safe_dump(categories))

        for i, tool in enumerate(tools):
            (tools_dir / f"tool-{i}.yml").write_text(yaml.safe_dump(tool))

        return categories_file, tools_dir

    return setup
