const helpers = require('../helpers');
const AnotherListCollectorPage = require('../generated_pages/list_collector/another-list-collector-block.page.js');
const AnotherListCollectorAddPage = require('../generated_pages/list_collector/another-list-collector-block-add.page.js');
const AnotherListCollectorEditPage = require('../generated_pages/list_collector/another-list-collector-block-edit.page.js');
const AnotherListCollectorRemovePage = require('../generated_pages/list_collector/another-list-collector-block-remove.page.js');
const IntroductionPage = require('../generated_pages/list_collector/introduction.page.js');
const ListCollectorPage = require('../generated_pages/list_collector/list-collector.page.js');
const ListCollectorAddPage = require('../generated_pages/list_collector/list-collector-add.page.js');
const ListCollectorEditPage = require('../generated_pages/list_collector/list-collector-edit.page.js');
const ListCollectorRemovePage = require('../generated_pages/list_collector/list-collector-remove.page.js');
const NextInterstitialPage = require('../generated_pages/list_collector/next-interstitial.page.js');
const SummaryPage = require('../generated_pages/list_collector/summary.page.js');

describe('@watch List Collector', function() {

  describe('List Collector Without Variants', function() {
    beforeEach('Load the survey', function() {
      return helpers.openQuestionnaire('test_list_collector.json');
    });

    it('Given a normal journey through the list collector, the user is able to add / remove / edit members of the household', function() {
      return browser
        .click(IntroductionPage.getStarted())
        .click(ListCollectorPage.yes())
        .click(ListCollectorPage.submit())
        .setValue(ListCollectorAddPage.firstName(), 'Mark')
        .setValue(ListCollectorAddPage.lastName(), 'Twain')
        .click(ListCollectorAddPage.submit())
        .click(ListCollectorPage.yes())
        .click(ListCollectorPage.submit())
        .setValue(ListCollectorAddPage.firstName(), 'Samuel')
        .setValue(ListCollectorAddPage.lastName(), 'Clemens')
        .click(ListCollectorAddPage.submit())
        .click(ListCollectorPage.yes())
        .click(ListCollectorPage.submit())
        .setValue(ListCollectorAddPage.firstName(), 'Olivia')
        .setValue(ListCollectorAddPage.lastName(), 'Clemens')
        .click(ListCollectorAddPage.submit())
        .click(ListCollectorPage.yes())
        .click(ListCollectorPage.submit())
        .setValue(ListCollectorAddPage.firstName(), 'Suzy')
        .setValue(ListCollectorAddPage.lastName(), 'Clemens')

        // Correct name spelling, ensure reflected in summary

        .click(ListCollectorAddPage.submit())
        .click(ListCollectorPage.yes())
        .click(ListCollectorPage.submit())
        .setValue(ListCollectorAddPage.firstName(), 'Clara')
        .setValue(ListCollectorAddPage.lastName(), 'Clemens')
        .click(ListCollectorAddPage.submit())
        .click(ListCollectorPage.yes())
        .click(ListCollectorPage.submit())
        .setValue(ListCollectorAddPage.firstName(), 'Jean')
        .setValue(ListCollectorAddPage.lastName(), 'Clemens')
        .click(ListCollectorAddPage.submit())

        // Remove Mark Twain - Ensure list is empty

    });
  });
});
