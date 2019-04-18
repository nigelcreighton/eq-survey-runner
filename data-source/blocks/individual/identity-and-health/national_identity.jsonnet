local placeholders = import '../../../lib/placeholders.libsonnet';
local rules = import '../../../lib/rules.libsonnet';

local question(proxyOptions, regionOptions) = {
  id: 'national-identity-question',
  title: proxyOptions.title,
  type: 'General',
  definitions: [
    {
      title: "What do we mean by “national identity”?",
      content: proxyOptions.definitionContent
    },
  ],
  answers: [
    {
      id: 'national-identity-answer',
      mandatory: true,
      type: 'Checkbox',
    } + regionOptions,
  ],
};

local nonProxyOptions = {
  title: 'How would you describe your national identity?',
  definitionContent: [
    {
      description: 'National identity is not dependent on your ethnic group or citizenship.'
    },
    {
      description: 'It is about the country or countries where you feel you belong or think of as home.'
    }
  ]
};
local isProxyOptions = {
  title: {
    text: 'How would <em>{person_name}</em> describe their national identity?',
    placeholders: [
      placeholders.personName,
    ],
  },
  definitionContent: [
    {
      description: 'National identity is not dependent on their ethnic group or citizenship.'
    },
    {
      description: 'It is about the country or countries where they feel they belong or think of as home.'
    }
  ]
};

local englandOptions = {
  options: [
    {
      label: 'English',
      value: 'English'
    },
    {
      label: 'Welsh',
      value: 'Welsh'
    },
    {
      label: 'Scottish',
      value: 'Scottish'
    },
    {
      label: 'Northern Irish',
      value: 'Northern Irish'
    },
    {
      label: 'British',
      value: 'British'
    },
    {
      label: 'Other',
      value: 'Other',
      detail_answer: {
        id: 'national-identity-answer-other',
        type: 'TextField',
        mandatory: false,
        label: 'Please describe your national identity',
      }
    }
  ]
};

local walesOptions = {
  options: [
    {
      label: 'Welsh',
      value: 'Welsh'
    },
    {
      label: 'English',
      value: 'English'
    },
    {
      label: 'Scottish',
      value: 'Scottish'
    },
    {
      label: 'Northern Irish',
      value: 'Northern Irish'
    },
    {
      label: 'British',
      value: 'British'
    },
    {
      label: 'Other',
      value: 'Other',
      detail_answer: {
        id: 'national-identity-answer-other',
        type: 'TextField',
        mandatory: false,
        label: 'Please describe your national identity'
      }
    }
  ]
};

{
  type: 'Question',
  id: 'national-identity',
  question_variants: [
    {
      question: question(nonProxyOptions, englandOptions),
      when: [rules.proxyNo, rules.regionNotWales]
    },
    {
      question: question(isProxyOptions, englandOptions),
      when: [rules.proxyYes, rules.regionNotWales]
    },
    {
      question: question(nonProxyOptions, walesOptions),
      when: [rules.proxyNo, rules.regionWales]
    },
    {
      question: question(isProxyOptions, walesOptions),
      when: [rules.proxyYes, rules.regionWales]
    }
  ]
}
