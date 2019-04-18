local placeholders = import '../../../lib/placeholders.libsonnet';
local rules = import '../../../lib/rules.libsonnet';

local question(title, regionOptions) = {
  id: 'a-level-question',
  title: title,
  guidance: regionOptions.guidance,
  type: 'MutuallyExclusive',
  mandatory: true,
  answers: [
    {
      id: 'a-level-answer',
      mandatory: false,
      type: 'Checkbox',
      options: regionOptions.answerOptions
    },
    {
      id: 'a-level-answer-exclusive',
      type: 'Checkbox',
      mandatory: false,
      options: [
        {
          label: 'None of these apply',
          value: 'None of these apply',
          description: 'Questions on GCSEs and equivalents will follow',
        }
      ]
    }
  ]
};

local nonProxyTitle = 'Have you achieved an AS, A level or equivalent qualification?';
local proxyTitle = {
  text: 'Has <em>{person_name}</em> achieved an AS, A level or equivalent qualification?',
  placeholders: [
    placeholders.personName
  ]
};

local commonOptions = [
  {
    label: '2 or more A levels',
    value: '2 or more A levels',
    description: 'Include 4 or more AS levels'
  },
  {
    label: '1 A level',
    value: '1 A level',
    description: 'Include 2 to 3 AS levels'
  },
  {
    label: '1 AS level',
    value: '1 AS level'
  }
];

local englandOptions = {
  guidance: {
    content: [
      {
        title: 'Include equivalent qualifications achieved anywhere outside England and Wales'
      }
    ]
  },
  answerOptions: commonOptions
};
local walesOptions = {
  guidance: {
    content: [
      {
        title: 'Include equivalent qualifications achieved anywhere outside Wales and England'
      }
    ]
  },
  answerOptions: commonOptions + [
        {
          label: 'Advanced Welsh Baccalaureate',
          value: 'Advanced Welsh Baccalaureate'
        }
      ]
};

{
  type: 'Question',
  id: 'a-level',
  question_variants: [
    {
      question: question(nonProxyTitle, englandOptions),
      when: [rules.proxyNo, rules.regionNotWales],
    },
    {
      question: question(proxyTitle, englandOptions),
      when: [rules.proxyYes, rules.regionNotWales],
    },
    {
      question: question(nonProxyTitle, walesOptions),
      when: [rules.proxyNo, rules.regionWales],
    },
    {
      question: question(proxyTitle, walesOptions),
      when: [rules.proxyYes, rules.regionWales],
    }
  ]
}
