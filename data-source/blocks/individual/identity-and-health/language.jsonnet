local placeholders = import '../../../lib/placeholders.libsonnet';
local rules = import '../../../lib/rules.libsonnet';

local question(proxyOptions, regionOptions) = {
  id: 'language-question',
  title: proxyOptions.title,
  type: 'General',
  definitions: proxyOptions.definitionContent,
  answers: [
    {
      id: 'language-answer',
      mandatory: true,
      type: 'Radio',
    } + regionOptions,
  ],
};

local nonProxyOptions = {
  title: 'What is your main language?',
  definitionContent: [
    {
      title: 'What do we mean by “main language”?',
      content: [
        {
          description: 'Your main language is the language you use most naturally. It could be the language you use at home.',
        },
      ],
    },
  ],
};
local isProxyOptions = {
  title: {
    text: 'What is <em>{person_name_possessive}</em> main language?',
    placeholders: [
      placeholders.personNamePossessive,
    ],
  },
  definitionContent: [
    {
      title: 'What do we mean by “main language”?',
      content: [
        {
          description: 'Your main language is the language they use most naturally. It could be the language they use at home.',
        },
      ],
    },
  ],
};

local englandOptions = {
  options: [
    {
      label: 'English',
      value: 'English',
    },
    {
      label: 'Other',
      value: 'Other',
      description: 'Including British Sign Language',
      detail_answer: {
        id: 'language-answer-other',
        type: 'TextField',
        mandatory: false,
        label: 'Please specify main language',
      },
    },
  ],
};

local walesOptions = {
  options: [
    {
      label: 'English or Welsh',
      value: 'English or Welsh',
    },
    {
      label: 'Other',
      value: 'Other',
      description: 'Including British Sign Language',
      detail_answer: {
        id: 'language-answer-other',
        type: 'TextField',
        mandatory: false,
        label: 'Please specify main language',
      },
    },
  ],
};

{
  type: 'Question',
  id: 'language',
  question_variants: [
    {
      question: question(nonProxyOptions, englandOptions),
      when: [rules.proxyNo, rules.regionNotWales],
    },
    {
      question: question(isProxyOptions, englandOptions),
      when: [rules.proxyYes, rules.regionNotWales],
    },
    {
      question: question(nonProxyOptions, walesOptions),
      when: [rules.proxyNo, rules.regionWales],
    },
    {
      question: question(isProxyOptions, walesOptions),
      when: [rules.proxyYes, rules.regionWales],
    },
  ],
  routing_rules: [
    {
      goto: {
        block: 'national-identity',
        when: [
          {
            id: 'language-answer',
            condition: 'equals',
            value: 'English',
          },
        ],
      },
    },
    {
      goto: {
        block: 'national-identity',
        when: [
          {
            id: 'language-answer',
            condition: 'equals',
            value: 'English or Welsh',
          },
        ],
      },
    },
    {
      goto: {
        block: 'english',
      },
    },
  ],
}
