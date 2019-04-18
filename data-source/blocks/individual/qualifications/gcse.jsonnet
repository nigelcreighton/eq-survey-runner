local placeholders = import '../../../lib/placeholders.libsonnet';
local rules = import '../../../lib/rules.libsonnet';

local question(title, regionOptions) = {
  id: 'gcse-question',
  title: title,
  type: 'MutuallyExclusive',
  mandatory: true,
  guidance: regionOptions.guidance,
  answers: [
    {
      id: 'gcse-answer',
      mandatory: false,
      type: 'Checkbox',
      options: regionOptions.answerOptions,
    },
    {
      id: 'gcse-answer-exclusive',
      type: 'Checkbox',
      mandatory: false,
      options: [
        {
          label: 'None of these apply',
          value: 'None of these apply',
        },
      ],
    },
  ],
};

local nonProxyTitle = 'Have you achieved a GCSE or equivalent qualification?';
local proxyTitle = {
  text: 'Has <em>{person_name}</em> achieved a GCSE or equivalent qualification?',
  placeholders: [
    placeholders.personName,
  ],
};

local commonOptions = [
  {
    label: '5 or more GCSEs grades A* to C or 9 to 4',
    value: '5 or more GCSEs',
    description: 'Include 5 or more O level passes or CSEs grades 1',
  },
  {
    label: 'Any other GCSEs',
    value: 'Any other GCSEs',
    description: 'Include any other O levels or CSEs at any grades',
  },
  {
    label: 'Basic skills course',
    value: 'Basic skills course',
    description: 'Skills for life, literacy, numeracy and language',
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
    label: 'Intermediate or National Welsh Baccalaureate',
    value: 'Intermediate or National Welsh Baccalaureate'
  },
  {
    label: 'Foundation Welsh Baccalaureate',
    value: 'Foundation Welsh Baccalaureate'
  }
  ]
};

{
  type: 'Question',
  id: 'gcse',
  question_variants: [
    {
      question: question(nonProxyTitle, englandOptions),
      when: [rules.proxyNo, rules.regionNotWales]
    },
    {
      question: question(proxyTitle, englandOptions),
      when: [rules.proxyYes, rules.regionNotWales]
    },
    {
      question: question(nonProxyTitle, walesOptions),
      when: [rules.proxyNo, rules.regionWales]
    },
    {
      question: question(proxyTitle, walesOptions),
      when: [rules.proxyYes, rules.regionWales]
    }
  ],
  routing_rules: [
    {
      goto: {
        block: 'other-qualifications',
        when: [
          {
            id: 'apprenticeship-answer',
            condition: 'equals',
            value: 'No',
          },
          {
            id: 'degree-answer',
            condition: 'equals',
            value: 'No',
          },
          {
            id: 'gcse-answer-exclusive',
            condition: 'contains',
            value: 'None of these apply',
          },
          {
            id: 'a-level-answer-exclusive',
            condition: 'contains',
            value: 'None of these apply',
          },
          {
            id: 'nvq-level-answer-exclusive',
            condition: 'contains',
            value: 'None of these apply',
          },
        ],
      },
    },
    {
      goto: {
        group: 'employment-group',
      },
    },
  ],
}
