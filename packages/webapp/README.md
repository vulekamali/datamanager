
# 🏦 Vulekamali Front-end Webapp

[![](https://img.shields.io/badge/openup--content--starter-0.1.1-blue.svg)](https://github.com/OpenUpSA/react-webapp-starters)

**A decoupled React webapp connected to Jekyll via HTML data attributes and remote endpoints**

This is decoupled webapp is a temporary solution in order to ease the long term transition from Jekyll to a more integrated React based front-end system like Gatsby.

## Contributor instructions:

*If you have any questions about the following instructions please get in touch with us via [our core-team Slack workspace](https://openupsa.slack.com) (if you have access) or send an email to [schalk@openup.org.za](mailto:schalk@openup.org.za).*

If you've received a link to this specific README file it means that you are expected to only work on the Webapp logic and not require to understand or concern yourself with anything outside of the `/packages/webapp` folder.

### 🌱 1. Set up local environment

1. Clone the repository:
   - **1.1.** If you are a core contributor (have write access) then you can skip step `1.2` and `1.3` and directly clone the project via `git clone https://github.com/vulekamali/static-budget-portal`.
   - **1.2.** Fork the repo on Github at https://github.com/vulekamali/static-budget-portal
   - **1.3** Clone the for you create via `git clone https://github.com/<-- YOUR_GITHUB_USERNAME -->/static-budget-portal`
2. Make sure you have the latest release of [NodeJS](https://nodejs.org/en/) installed.
3. Make sure you have the latest release of [Yarn](https://yarnpkg.com/en/docs/install) installed.
4. Run `yarn` in the root folder of the repository to install all dependancies (not the `/packages/webapp` folder).

### 💓 3. Contribute 

1. Please familiarise yourself with **all** of the following before proceding:
   - The [file and folder conventionsused in this project](#) 
   - [This project's tech-stack](#) underpinning this project.
   - How to [sandbox changes you are making in this project](#).
2. Implement desired changes
3. Make sure that changes do not break any existing functionality by [testing existing code in this project](#)
4. Get user-facing changes signed-off by brand manager:
   - Run `yarn build:storybook` from `/packages/webapp`
   - Upload drag and drop the `/packages/webapp/storybook-build` into [https://app.netlify.com/drop](https://app.netlify.com/drop).
   - Once uploaded it will provide you with a unique URL.
   - Share the following message in the `treasury-dev` channel in the OpenUp workspace: `@Matt please confirm that you are happy with the <-- FEATURE_NAME_HERE --> at <-- NETLIFY_DROP_URL_HERE -->`
   - If changes are requested then follow the above process again.
   - Once you have sign-off from the brand manager you can proceed with step 4 below.

### 🚀 4. Make a pull request

1. If you are making a public pull request (i.e. you do not have write access) use the [forking Git workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow).
2. If you are a project contributor (.e. you have write access) use the [feature branch Git workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow).
3. Make a [pull request](https://www.atlassian.com/git/tutorials/making-a-pull-request) via the [Github](#github) dashboard to the `master` branch.
4. The designated owner of the repository will automatically be tagged in all pull requests via the `docs/CODEOWNERS` file.
5. Once your code has been accepted and merged into `master` [Netlify](#netlify) will automatically deploy the changes to [khetha.org.za](http://khetha.org.za).
