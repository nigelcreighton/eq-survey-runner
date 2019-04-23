local placeholders = import '../../../lib/placeholders.libsonnet';
local rules = import '../../../lib/rules.libsonnet';

local question(proxyOptions) = {
  id: 'disability-limitation-question',
  title: proxyOptions.title,
  definitions: proxyOptions.definitionContent,
  type: 'General',
  answers: [
    {
      id: 'disability-limitation-answer',
      mandatory: true,
      options: [
        {
          label: 'Yes, a lot',
          value: 'Yes, a lot',
        },
        {
          label: 'Yes, a little',
          value: 'Yes, a little',
        },
        {
          label: 'Not at all',
          value: 'Not at all',
        },
      ],
      type: 'Radio',
    },
  ],
};

local nonProxyOptions = {
  title: 'Do any of your conditions or illnesses reduce your ability to carry out day-to-day activities?',
  definitionContent: [
    {
      title: 'What do we mean by “reduce your ability”?',
      content: [
        {
          description: 'We mean whether your health condition or illness currently affects your ability to carry out day-to-day activities.',
        },
        {
          description: 'Consider whether you are still affected while receiving any treatment, medication or using any devices for your condition or illness.',
        },
        {
          description: 'For example, if you need a hearing aid and by using the device you experience no restriction in carrying out your day-to-day activities, then you should select “Not at all”.',
        },
        {
          description: 'You should select “Yes, a lot” if you usually need some level of support from family members, friends or personal social services for most normal daily activities.',
        },
      ],
    },
  ],
};
local isProxyOptions = {
  title: {
    text: 'Does any of <em>{person_name_possessive}</em> conditions or illnesses reduce their ability to carry out day-to-day activities?',
    placeholders: [
      placeholders.personNamePossessive,
    ],
  },
  definitionContent: [
    {
      title: 'What do we mean by “reduce their ability”?',
      content: [
        {
          description: 'We mean whether their health condition or illness currently affects their ability to carry out day-to-day activities.',
        },
        {
          description: 'Consider whether they are still affected while receiving any treatment, medication or using any devices for their condition or illness.',
        },
        {
          description: 'For example, if they need a hearing aid and by using the device they experience no restriction in carrying out their day-to-day activities, then you should select “Not at all”.',
        },
        {
          description: 'You should select “Yes, a lot” if they usually need some level of support from family members, friends or personal social services for most normal daily activities.',
        },
      ],
    },
  ],
};

{
  type: 'Question',
  id: 'disability-limitation',
  question_variants: [
    {
      question: question(nonProxyOptions),
      when: [rules.proxyNo],
    },
    {
      question: question(isProxyOptions),
      when: [rules.proxyYes],
    },
  ],
}
