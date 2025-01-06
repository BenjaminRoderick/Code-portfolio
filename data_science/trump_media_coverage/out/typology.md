# Typology for the Trump dataset

## Primary Categories

### Election (ELEC)

Articles related to compaign and election results.
       
1. **Rules for inclusion:**
    - Biden vs Trump or Harris vs Trump campaign.
    - Supporters/ endorsers.
    - Polls and bettings.
    - Articles related to Trump's rise to power/ second term.
    - Post-election content like Harris, Trump or their supporters' reactions.
           
2. **Rules for exclusion:**
    - Trump's legal troubles and its impact on his election.
    - Articles about Trump's family members.
    - Articles on policies.
           
3. **Examples from data:**
    - "It's the last day of the 2024 campaign."
    - "Trump wins a second term."
    - "Steve Schwarzman says Trump would be an 'efficient and effective' president this time"
    - "Fact check: Trump, allies push allegations of election 'cheating' in Pennsylvania"

### Personal (PERS)

Articles related to Trump's personal image, legal troubles, and public behaviour.
       
1. **Rules for inclusion:**
    - Articles on Trump's criminal charges and court cases.
    - Behaviour in public conferences/meetings.
    - Lashing out, misconduct and lies.
    - Personal information including hobbies, family.
           
2. **Rules for exclusion:**
    - Trump's appointments to his government.
    - Racism, sexism, LGBTQ or immigration related articles.
    - Artciles on Harris or Biden.

3. **Examples from data:**
    - "Did you need another reminder that Donald Trump watches TV?"
    - "Eric Adams dodges questions about potential Trump pardon"
    - "Trump, using violent language, attacks 'war hawk' Liz Cheney"
           
### Internal Politics (INT-POLI)

Articles related Trump's government structure, cabinet, and bipartisanship.
       
1. **Rules for inclusion:**
    - Trump's appointments to his government.
    - Cabinet structure.
    - Elon Musk
    - Cooperation/Opposition with other American politicians.
           
2. **Rules for exclusion:**
    - Articles on Trump and international politicians.
    - Ukraine war or Isreal-Palestine war.
    - Policies
    - Personal information.
           
3. **Examples from data:**
    - "Tracking who Trump has named to serve in his Cabinet"
    - "Trump announces oil executive Chris Wright as his pick for energy secretary"
    - "Trump announces Elon Musk to lead 'Department of Government Efficiency' with Ramaswamy"
    - "Project 2025 is infiltrating the Trump administration already"
           
### Social (SOCIO)

Articles related Trump's LGBTQ views, racism, and immigrant issues.
       
1. **Rules for inclusion:**
    - Trump's LGBTQ views and homophobia.
    - Racism and sexism.
    - Immigration policies, border and deportation
           
2. **Rules for exclusion:**
    - Harris, Biden or other politicians view on above listed topics.
    - War related content.
    - Trump's legal troubles.
           
3. **Examples from data:**
    - "Latino political strategist responds to Puerto Rico jokes at Trump MSG rally"
    - "Trump Seeks Mass Deportations, Workplace Raids May Not Help Much"
    - "Did Trump win in 2024 because of racism? It’s complicated."
           
### International (INTER)

Articles related to international relations, defense and war.
       
1. **Rules for inclusion:**
    - Ukraine-Russia war, Putin, and Zelenskyy.
    - Isreal-Palestine war and Hamas.
    - Trump's relation with international politicians.
    - China, India, and other countries.
           
2. **Rules for exclusion:**
    - Trump's relation with American politicians.
    - Internal policy related content.
    - Personal information.
           
3. **Examples from data:**
    - "50 European Leaders Assess How Trump Will Affect Their Fortunes"
    - "China's Xi sets boundaries for Trump with 4 'red lines'"
    - "Putin praises Trump, says he's ready to talk to him"
           
### Climate (CLIM)

Articles related climate policy.
       
1. **Rules for inclusion:**
    - Climate policies.
    - Climate related pact with international countries.
    - Climate views.
           
2. **Rules for exclusion:**
    - Health related content.
    - Other politicians view on climate and not Trump's specifically or his government. 
    - Any article that does not mention climate policies/issues explicitly.
           
3. **Examples from data:**
    - "Giving Up on Climate Action in a Second Trump Term Isn’t an Option"
    - "Trump likely to target climate measures that are making the most difference"
    - "Even Exxon’s CEO Doesn’t Want Trump to Pull Out of the Paris Climate Agreement"
           
### Economy (ECON)

Articles related to inflation, finance, debt, technology and other industries.
       
1. **Rules for inclusion:**
    - Finance, stock market, and trading. 
    - Inflation and debt.
    - Economic policies.
    - Technology and other industries that drive the country's economy.
           
2. **Rules for exclusion:**
    - Articles that don't explicitly mention economic related topics mentioned above.

3. **Examples from data:**
    - "Here's what Trump 2.0 means for the economy"
    - "Young Black and Latino men say they chose Trump because of the economy and jobs"
    - "Elon Musk Keeps Saying Trump Will Tank the Economy"
    - "Trump Will Try to Stop the TikTok Ban, but How?"
           
### Health (HEAL)

Articles related to public health, abortion, and healthcare research and organizations.
       
1. **Rules for inclusion:**
    - Abortion and pro-life related topics
    - Public institutes like hospitals, clinics and pharmacy.
    - Pharmaceutical companies and other healthcare compagnies.
    - Vaccination, and medical products.
           
2. **Rules for exclusion:**
    - Sexism
    - Biden/Harris policies on healthcare and abortion.
           
3. **Examples from data:**
    - "What a 2nd Trump term may look like for health care issues including ACA, abortion"
    - "What to know about Dr. Oz as Trump picks him to oversee Medicare, Medicaid"
    - "‘We’re Not Single Issue Voters.’ Trump Bets Abortion Isn’t Key to Suburban Women Vote"

## Handling Ambiguous Cases

1. **Relating to Sentiment**
    - An article is considered to have a neutral sentiment when it consists solely of statements and descriptions without using
      negative or positive keywords.
    - Critiques of anything related to Trump is a critique of Trump, and thus negative sentiment.

2. **Context Rule**
    - When the title of the article is too ambiguous, use the blurb, then follow the link if still unsure.
    - Use the most specific category when hesitating between two options.
