local placeholders = import '../../../lib/placeholders.libsonnet';
local rules = import '../../../lib/rules.libsonnet';

local question(title, regionOptions) = {
  id: 'degree-question',
  title: title,
  type: 'General',
  guidance: regionOptions.guidance,
  answers: [
    {
      id: 'degree-answer',
      mandatory: true,
      type: 'Radio',
      options: [
        {
          label: 'Yes',
          value: 'Yes',
          description: 'For example degree, foundation degree, HND or HNC, NVQ level 4 and above, teaching or nursing',
        },
        {
          label: 'No',
          value: 'No',
          description: 'Questions on other NVQs, A levels, GCSEs and equivalents will follow',
        },
      ],
    },
  ],
};

local nonProxyTitle = 'Have you achieved a qualification at degree level or above?';
local proxyTitle = {
  text: 'Has <em>{person_name}</em> achieved a qualification at degree level or above?',
  placeholders: [
    placeholders.personName,
  ],
};

local englandOptions = {
  guidance: {
    content: [
      {
        title: 'Include equivalent qualifications achieved anywhere outside England and Wales',
      },
    ],
  },
};
local walesOptions = {
  guidance: {
    content: [
      {
        title: 'Include equivalent qualifications achieved anywhere outside Wales and England',
      },
    ],
  },
};

{
  type: 'Question',
  id: 'degree',
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
    },
  ],
}
