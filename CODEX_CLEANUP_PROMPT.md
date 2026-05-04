# GO2CUP Cleanup Pass

Repository goal:
This is a static HTML site for GO2CUP, an independent fan-built World Cup 2026 travel and fan intelligence hub.

Important rules:
- Do not redesign pages.
- Do not rewrite page content unless needed for link clarity or legal/trust cleanup.
- Preserve existing CSS and visual style.
- Do not convert to React.
- Do not add frameworks.
- Do not delete pages.
- Use relative links for internal GitHub-hosted pages.
- Keep all host city pages inside /host-cities/.

Audit first. Do not edit files in the first pass.

Audit these items:

1. Host city inventory
Confirm all 16 host city pages exist inside /host-cities/:
- atlanta.html
- boston-foxborough.html
- dallas.html
- guadalajara.html
- houston.html
- kansas-city.html
- los-angeles.html
- mexico-city.html
- miami.html
- monterrey.html
- new-york-new-jersey.html
- philadelphia.html
- san-francisco-bay-area.html
- seattle.html
- toronto.html
- vancouver.html

2. FBO/private aviation cleanup
Search all files for:
- go2cup#fbo
- FBO
- Private Aviation
- VIP & Private Aviation

Return file names, line numbers, and exact text found.
Do not replace yet.

3. Internal city navigation
Find all links inside host city pages that point to:
https://mainentry.net/go-2-cup/

Recommend relative replacements using this pattern:
../host-cities/city-name.html

Do not replace yet.

4. CTA audit
Find all buttons or links for:
- Get Free Fan Guide
- Free Fan Guide
- newsletter
- World Cup news
- partner resources
- VIP

Recommend where each should point.

Main lead magnet URL:
https://mainentry.net/go2cup-fan-survival-guide

Partner resources page:
../partner-resources.html

5. Footer and disclaimer audit
Check whether every page has:
- independent from FIFA disclaimer
- affiliate disclosure if affiliate links appear
- verify schedules, prices, tickets, travel rules with official sources
- Maria/MainEntry/GO2CUP brand consistency

6. Risky claim audit
Flag claims that should be softened or verified, especially:
- exact prices
- exact match counts
- official shuttle language
- guaranteed transport language
- safety claims
- visa/ESTA costs
- stadium capacities
- match or ceremony claims
- “official” wording

Output:
Return a clean audit report with:
- critical fixes
- recommended fixes
- optional improvements
- files affected
- suggested next prompt for the actual cleanup edit pass
