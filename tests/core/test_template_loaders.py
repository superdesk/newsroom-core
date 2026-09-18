import pytest
import jinja2
import pathlib
import tempfile

from newsroom.template_loaders import LocaleTemplateLoader, set_template_locale


async def test_load_template_with_locale():
    template_data = {
        "test.html": "default template",
        "test.fr.html": "fr template",
        "test.en.html": "en template",
        "with_layout.fr.html": "{% extends 'test.html' %}",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        for filename, data in template_data.items():
            with open(pathlib.Path(tmpdir).joinpath(filename), "wt") as template:
                template.write(data)

        loader = LocaleTemplateLoader(tmpdir)
        env = jinja2.Environment(loader=loader)

        assert "default template" == env.get_template("test.html").render()

        assert "fr template" == env.get_template("test.fr.html").render()

        assert "en template" == env.get_template("test.en.html").render()

        set_template_locale("en")

        assert "en template" == env.get_template("test.html").render()

        assert "fr template" == env.get_template("test.fr.html").render()

        set_template_locale("fr")

        assert "fr template" == env.get_template("test.html").render()

        assert "en template" == env.get_template("test.en.html").render()

        assert "fr template" == env.get_template("with_layout.html").render()

        set_template_locale("en")

        assert "en template" == env.get_template("test.html").render()

        set_template_locale("fi")

        assert "default template" == env.get_template("test.html").render()

        set_template_locale()

        assert "default template" == env.get_template("test.html").render()

        with pytest.raises(jinja2.TemplateNotFound):
            env.get_template("missing.html").render()
