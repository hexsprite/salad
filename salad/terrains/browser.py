from lettuce import before, world, after
from splinter.browser import Browser
from salad.logger import logger
import os

@before.all
def setup_master_browser():
    try:
        browser = world.drivers[0]
        remote_url = world.remote_url
    except AttributeError, IndexError:
        browser = 'firefox'
        remote_url = None

    try:
        capabilities = world.remote_capabilities
    except AttributeError:
        capabilities = {}
    world.master_browser = setup_browser(browser, remote_url, **capabilities)
    world.browser = world.master_browser


def setup_browser(browser, url=None, **capabilities):
    logger.info("Setting up browser %s..." % browser)
    browser = os.environ.get('LETTUCE_BROWSER', browser)

    try:
        if url:
            logger.warn(capabilities)
        # support sauce config via SELENIUM_DRIVER
        # to support use via Jenkins Sauce plugin
        is_sauce = 'SELENIUM_DRIVER' in os.environ
        if is_sauce:
            driver_info = dict(
                [v.split('=', 2)
                for v in os.environ['SELENIUM_DRIVER'].split('?')[1].split('&')
            ])
            logger.info('Sauce configuration detected')
            desired_capabilities = {}
            desired_capabilities['browserName'] = driver_info['browser']
            desired_capabilities['version'] = driver_info['browser-version']
            desired_capabilities['platform'] = driver_info['os']
            url = "http://%s:%s@%s:%s/wd/hub" % (
                driver_info['username'], driver_info['access-key'],
                os.environ.get('SELENIUM_HOST', 'ondemand.saucelabs.com'),
                os.environ.get('SELENIUM_PORT', 80))
            browser = Browser('remote', url=url, **desired_capabilities)
        elif url:
            browser = Browser('remote', url=url,
                    browser=browser, **capabilities)
        else:
            browser = Browser(browser)
    except Exception as e:
        logger.warn("Error starting up %s: %s" % (browser, e))
        raise
    return browser


@before.each_scenario
def clear_alternative_browsers(step):
    world.browser = world.master_browser
    world.browsers = []


@after.each_scenario
def reset_to_parent_frame(step):
    if hasattr(world, "parent_browser"):
        world.browser = world.parent_browser


@after.each_scenario
def restore_browser(step):
    for browser in world.browsers:
        teardown_browser(browser)


@after.all
def teardown_master_browser(total):
    teardown_browser(world.master_browser)

def teardown_browser(browser):
    name = browser.driver_name
    logger.info("Tearing down browser %s..." % name)
    try:
        browser.quit()
    except Exception as e:
        logger.warn("Error tearing down %s: %s" % (name, e))
