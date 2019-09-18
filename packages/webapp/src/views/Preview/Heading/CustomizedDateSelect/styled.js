import styled from 'styled-components';

import { Select } from '@material-ui/core';

const CustomizedForm = styled.div`
  margin-right: 8px;
  width: 100%;

  @media screen and (min-width: 600px) {
    width: auto;
  }
`;

const SelectPreviewDate = styled(Select)`
  && {
    width: 100%;
    margin-right: 8px;

    & .disabled {
      color: rgba(0, 0, 0, 0.26);
    }

    & .icon {
      color: rgba(0, 0, 0, 0.26);
      margin-right: 10px;

      @media screen and (min-width: 600px) {
        margin-right: 16px;
      }
    }

    & .selectMenu {
      background: #d8d8d8;
      border-radius: 3px;
      padding: 13.5px 14px;
      font-size: 14px;
      font-weight: 700;
      line-height: 120%;

      @media screen and (min-width: 600px) {
        font-size: 20px;
        padding: 20px;
      }
    }

    @media screen and (min-width: 600px) {
      width: 185px;
    }
  }
`;


export {
  CustomizedForm,
  SelectPreviewDate
}

export default {
  CustomizedForm,
  SelectPreviewDate
}
