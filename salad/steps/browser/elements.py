from lettuce import step, world
from salad.tests.util import assert_equals_with_negate, assert_with_negate, parsed_negator
from salad.steps.browser.finders import ELEMENT_FINDERS, ELEMENT_THING_STRING, _get_visible_element
from splinter.exceptions import ElementDoesNotExist

# Find and verify that elements exist, have the expected content and attributes (text, classes, ids)


@step(r'should( not)? see "(.*)" (?:somewhere|anywhere) in (?:the|this) page')
def should_see_in_the_page(step, negate, text):
    assert_with_negate(text in world.browser.html, negate)


@step(r'should( not)? see (?:the|a) link (?:called|with the text) "(.*)"')
def should_see_a_link_called(step, negate, text):
    assert_with_negate(len(world.browser.find_link_by_text(text)) > 0, negate)


@step(r'should( not)? see (?:the|a) link to "(.*)"')
def should_see_a_link_to(step, negate, link):
    assert_with_negate(len(world.browser.find_link_by_href(link)) > 0, negate)


class ExistenceStepsFactory(object):
    def __init__(self, finders, step_pattern, test_function):
        self.finders = finders
        self.pattern = step_pattern
        self.test = test_function
        self.make_steps()

    def make_steps(self):
        for finder_string, finder_function in self.finders.iteritems():
            self.make_step(finder_string, finder_function)

    def make_step(self, finder_string, finder_function):
        # NOTE: This *MUST* be seperate from make_steps or reusing the loop
        # variables there will result in every step being the same
        @step(self.pattern % (ELEMENT_THING_STRING, finder_string))
        def _visible_step(step, negate, pick, find_pattern, *args):
            try:
                element = _get_visible_element(finder_function, pick, find_pattern)
            except ElementDoesNotExist:
                assert parsed_negator(negate)
                element = None
            self.test(element, negate, *args)

        self.wait_pattern = self.pattern + ' within (\d+) seconds'
        @step(self.wait_pattern % (ELEMENT_THING_STRING, finder_string))
        def _visible_wait_step(step, negate, pick, find_pattern, *args):
            wait_time = int(args[-1])
            try:
                element = _get_visible_element(finder_function, pick,
                        find_pattern, wait_time=wait_time)
            except ElementDoesNotExist:
                assert parsed_negator(negate)
                element = None
            self.test(element, negate, args[:-1])


visibility_pattern = r'should( not)? see (?:the|a|an)( first| last)? %s %s'
def visibility_test(element, negate, *args):
    assert_with_negate(element, negate)


contains_pattern = r'should( not)? see that the( first| last)? %s %s contains "(.*)"'
def contains_test(element, negate, *args):
    content = args[0]
    assert_with_negate(content in element.text, negate)


contains_exactly_pattern = r'should( not)? see that the( first| last)? %s %s (?:is|contains) exactly "(.*)"'
def contains_exactly_test(element, negate, *args):
    content = args[0]
    assert_equals_with_negate(content, element.text, negate)

attribute_pattern = r'should( not)? see that the( first| last)? %s %s has (?:an|the) attribute (?:of|named|called) "(\w*)"$'
def attribute_test(element, negate, *args):
    attribute = args[0]
    assert_with_negate(element[attribute] != None, negate)

attribute_value_pattern = r'should( not)? see that the( first| last)? %s %s has (?:an|the) attribute (?:of|named|called) "(.*)" with(?: the)? value "(.*)"'
def attribute_value_test(element, negate, *args):
    attribute = args[0]
    value = args[1]
    assert_equals_with_negate(element[attribute], value, negate)

ExistenceStepsFactory(ELEMENT_FINDERS, visibility_pattern, visibility_test)
ExistenceStepsFactory(ELEMENT_FINDERS, contains_pattern, contains_test)
ExistenceStepsFactory(ELEMENT_FINDERS, contains_exactly_pattern, contains_exactly_test)
ExistenceStepsFactory(ELEMENT_FINDERS, attribute_pattern, attribute_test)
ExistenceStepsFactory(ELEMENT_FINDERS, attribute_value_pattern, attribute_value_test)
