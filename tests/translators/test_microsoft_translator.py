# -*- coding: utf8 -*-
import unittest
from unittest import TestCase
from python_translators.translators.microsoft_translator import MicrosoftTranslator
from python_translators.translation_query import TranslationQuery
from python_translators.factories.microsoft_translator_factory import (
    MicrosoftTranslatorFactory,
)


class TestMicrosoftTranslator(TestCase):
    def setUp(self):
        self.translators = {
            "en-nl": MicrosoftTranslatorFactory.build_with_context("en", "nl"),
            "nl-en": MicrosoftTranslatorFactory.build_with_context("nl", "en"),
            "es-en": MicrosoftTranslatorFactory.build_with_context("es", "en"),
            "de-en": MicrosoftTranslatorFactory.build_with_context("de", "en"),
            "en-de": MicrosoftTranslatorFactory.build_with_context("en", "de"),
        }

    def test_simple_translations(self):
        response = self.translators["en-nl"].translate(TranslationQuery(query="hello"))

        self.assertEqual(response.get_raw_translations()[0], "Hallo")

    def test_invalid_microsoft_key(self):
        self.assertRaises(Exception, MicrosoftTranslator, "<this is an invalid key>")

    def test_ca_translations(self):
        response = self.translators["nl-en"].translate(
            TranslationQuery(
                before_context="De directeur", query="treedt af", after_context=""
            )
        )
        translation = response.get_raw_translations()[0]
        self.assertIn(
            translation, ["shall resign", "resigns"]
        )  # was 'shall resign' but not anymore as of 2020

        response = self.translators["en-nl"].translate(
            TranslationQuery(
                before_context="Dark",
                query="matter",
                after_context="is an unidentified type of matter distinct from dark energy.",
            )
        )
        translation = response.get_raw_translations()[0]
        self.assertEqual("materie", translation)

    def test_unicode_outputs(self):
        response = self.translators["en-de"].translate(
            TranslationQuery(
                before_context="The ", query="lion", after_context="goes to the forest"
            )
        )

        self.assertEqual("Löwe", response.get_raw_translations()[0])

    def test_unicode_inputs(self):
        response = self.translators["de-en"].translate(TranslationQuery(query="Löwe"))
        print(response.get_raw_translations()[0])
        self.assertEqual("lion", response.get_raw_translations()[0].lower())

    def test_html_chars(self):
        response = self.translators["nl-en"].translate(
            TranslationQuery(query="m'n maat")
        )


if __name__ == "__main__":
    unittest.main()
