import {
  Typography,
  Select,
} from '@material-ui/core';

import styled from 'styled-components';

const Wrapper = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16px;
  margin-left: 16px;
  margin-bottom: 20px;

  @media screen and (min-width: 550px) {
    margin-right: 48px;
    margin-left: 48px;
  }

  @media screen and (min-width: 950px) {
    margin-bottom: 40px;
  }
`;

const BudgetContainer = styled.div`
  border-bottom: 1px solid #000;
  max-width: 1200px;
  padding-bottom: 16px;
  width: 100%;
  display: flex;
  flex-direction: column;

  @media screen and (min-width: 950px) {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 24px;
  }
`;

const BudgetHeadingAndShareIcon = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: right;
`;

const BudgetHeading = styled(Typography)`
  && {
    font-weight: 700;
    font-size: 18px;
    line-height: 120%;
    color: #000;
    text-transform: Capitalize;
    text-align: left;

    @media screen and (min-width: 950px) {
      white-space: nowrap;
      padding-right: 22px;
      font-size: 32px;
    }
  }
`;

const FormContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;

  @media screen and (min-width: 375px) {
    width: 100%;
    flex-wrap: wrap;
  }

  @media screen and (min-width: 950px) {
    width: auto;
    flex-wrap: nowrap;
    margin-top: 0;
  }
`;

const BudgetPhase = styled.div`
  @media screen and (min-width: 375px) {
    width: 60%;
  }

  @media screen and (min-width: 950px) {
    margin-right: 24px;
    width: auto;
  }
`;

const SelectStyledPhase = styled(Select)`
  && {
    background: #d8d8d8;
    border-radius: 3px;
    padding: 8px 12px 8px 16px;
    font-size: 14px;
    line-height: 120%;
    color: #000;

    & .selectMenu {
      padding-right: 32px;

      @media screen and (min-width: 950px) {
        padding-right: 56px;
      }
    }

    & .disabled {
      color: rgba(0, 0, 0, 0.26);
    }

    & .icon {
      color: rgba(0, 0, 0, 0.26);
    }

    @media screen and (min-width: 375px) {
      width: 100%;
    }

    @media screen and (min-width: 950px) {
      font-size: 20px;
      padding: 10px 16px;
      width: auto;
    }
  }
`;

const SelectStyled = styled(SelectStyledPhase)`
  && {
    @media screen and (min-width: 375px) {
      width: 35%;
    }

    @media screen and (min-width: 950px) {
      font-size: 20px;
      padding: 10px 16px;
      width: auto;
    }
  }
`;

const SpeedDialContainer = styled.div`
  margin-right: 8px;
`;

export {
  Wrapper,
  BudgetContainer,
  BudgetHeadingAndShareIcon,
  BudgetHeading,
  FormContainer,
  BudgetPhase,
  SelectStyled,
  SelectStyledPhase,
  SpeedDialContainer,
}

export default {
  Wrapper,
  BudgetContainer,
  BudgetHeadingAndShareIcon,
  BudgetHeading,
  FormContainer,
  BudgetPhase,
  SelectStyled,
  SelectStyledPhase,
  SpeedDialContainer,
}
