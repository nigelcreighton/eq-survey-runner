local placeholders = import '../../../lib/placeholders.libsonnet';
local rules = import '../../../lib/rules.libsonnet';

local question(title, regionOptions) = {
  id: 'nvq-level-question',
  title: title,
  type: 'MutuallyExclusive',
  guidance: regionOptions.guidance,
  mandatory: true,
  answers: [
    {
      id: 'nvq-level-answer',
      mandatory: false,
      type: 'Checkbox',
      options: [
        {
          label: 'NVQ level 3 or equivalent',
          value: 'NVQ level 3 or equivalent',
          description: 'For example BTEC National, OND or ONC, City and Guilds Advanced Craft',
        },
        {
          label: 'NVQ level 2 or equivalent',
          value: 'NVQ level 2 or equivalent',
          description: 'For example BTEC General, City and Guilds Craft',
        },
        {
          label: 'NVQ level 1 or equivalent',
          value: 'NVQ level 1 or equivalent',
        },
      ],
    },
    {
      id: 'nvq-level-answer-exclusive',
      type: 'Checkbox',
      mandatory: false,
      options: [
        {
          label: 'None of these apply',
          value: 'None of these apply',
          description: 'Questions on A levels, GCSEs and equivalents will follow',
        },
      ],
    },
  ],
};

local nonProxyTitle = 'Have you achieved an NVQ or equivalent qualification?';
local proxyTitle = {
  text: 'Has <em>{person_name}</em> achieved an NVQ or equivalent qualification?',
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
  id: 'nvq-level',
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
