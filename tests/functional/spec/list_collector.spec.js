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

function checkPeopleInList(peopleExpected) {
  let chain = browser.waitForVisible(ListCollectorPage.listLabel(1)).should.eventually.be.true;

  for (let i=1; i<=peopleExpected.length; i++) {
    chain = chain.then(() => {
      return browser.getText(ListCollectorPage.listLabel(i)).should.eventually.equal(peopleExpected[i-1])
    });
  }

  return chain;
}

describe('@watch List Collector', function() {

  describe('List Collector Without Variants', function() {
    before('Load the survey', function() {
      return helpers.openQuestionnaire('test_list_collector.json');
    });

    it('Given a normal journey through the list collector, the user is able to add members of the household', function() {
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
        .click(ListCollectorAddPage.submit());
    });

    it('Shows all of the household members in the summary', function() {
      const peopleExpected = ['Mark Twain', 'Samuel Clemens', 'Olivia Clemens', 'Suzy Clemens']
      return checkPeopleInList(peopleExpected)
    });

    it('Allows me to remove the first person (Mark Twain) from the summary', function() {
      return browser
        .click(ListCollectorPage.listRemoveLink(1))
        .click(ListCollectorRemovePage.yes())
        .click(ListCollectorRemovePage.submit())
    })

    it('Does not show Mark Twain anymore.', function() {
      return browser
        .getText(ListCollectorPage.listLabel(1)).should.not.eventually.have.string('Mark Twain')
    })

    it('Allows more people to be added', function() {
      browser
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
    });
  });
});
