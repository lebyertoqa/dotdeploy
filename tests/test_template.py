"""Tests for dotdeploy.template."""

import pytest
from pathlib import Path

from dotdeploy.template import (
    render,
    render_file,
    is_template,
    TemplateError,
    TEMPLATE_EXT,
)


def test_render_known_variable():
    result = render("Hello, {{ USER }}!", {"USER": "alice"})
    assert result == "Hello, alice!"


def test_render_multiple_variables():
    result = render("{{ A }} and {{ B }}", {"A": "foo", "B": "bar"})
    assert result == "foo and bar"


def test_render_unknown_variable_raises():
    with pytest.raises(TemplateError, match="Unknown template variable: 'MISSING'"):
        render("{{ MISSING }}", {})


def test_render_no_placeholders():
    text = "no placeholders here"
    assert render(text) == text


def test_render_whitespace_in_placeholder():
    result = render("{{  KEY  }}", {"KEY": "value"})
    assert result == "value"


def test_render_default_home_variable(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    result = render("home={{ HOME }}", {})
    # HOME default is Path.home() which may differ from env; just check no error
    assert "home=" in result


def test_render_file_basic(tmp_path):
    src = tmp_path / "bashrc.ddtpl"
    src.write_text("export USER={{ USER }}", encoding="utf-8")
    dest = tmp_path / "out" / ".bashrc"

    render_file(src, dest, {"USER": "bob"})

    assert dest.exists()
    assert dest.read_text() == "export USER=bob"


def test_render_file_creates_parent_dirs(tmp_path):
    src = tmp_path / "t.ddtpl"
    src.write_text("ok", encoding="utf-8")
    dest = tmp_path / "a" / "b" / "c" / "out.txt"

    render_file(src, dest, {})
    assert dest.exists()


def test_render_file_missing_source_raises(tmp_path):
    src = tmp_path / "nonexistent.ddtpl"
    dest = tmp_path / "out.txt"
    with pytest.raises(TemplateError, match="not found"):
        render_file(src, dest)


def test_render_file_unknown_variable_raises(tmp_path):
    src = tmp_path / "t.ddtpl"
    src.write_text("{{ GHOST }}", encoding="utf-8")
    dest = tmp_path / "out.txt"
    with pytest.raises(TemplateError, match="GHOST"):
        render_file(src, dest, {})


def test_is_template_true(tmp_path):
    p = tmp_path / f"bashrc{TEMPLATE_EXT}"
    assert is_template(p) is True


def test_is_template_false(tmp_path):
    p = tmp_path / "bashrc"
    assert is_template(p) is False
