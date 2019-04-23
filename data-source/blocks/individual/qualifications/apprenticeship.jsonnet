local placeholders = import '../../../lib/placeholders.libsonnet';
local rules = import '../../../lib/rules.libsonnet';

local question(title, regionOptions) = {
  id: 'apprenticeship-question',
  title: title,
  type: 'General',
  guidance: regionOptions.guidance,
  answers: [
    {
      id: 'apprenticeship-answer',
      mandatory: true,
      options: [
        {
          label: 'Yes',
          value: 'Yes',
          description: 'For example trade, advanced, foundation, modern',
        },
        {
          label: 'No',
          value: 'No',
        },
      ],
      type: 'Radio',
    },
  ],
};

local nonProxyTitle = 'Have you completed an apprenticeship?';
local proxyTitle = {
  text: 'Has <em>{person_name}</em> completed an apprenticeship?',
  placeholders: [
    placeholders.personName,
  ],
};

local englandOptions = {
  guidance: {
    content: [
      {
        title: 'Include equivalent apprenticeships completed anywhere outside England and Wales',
      },
    ],
  },
};
local walesOptions = {
  guidance: {
    content: [
      {
        title: 'Include equivalent apprenticeships completed anywhere outside Wales and England',
      },
    ],
  },
};

{
  type: 'Question',
  id: 'apprenticeship',
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
