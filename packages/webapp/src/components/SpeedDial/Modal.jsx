import React from 'react';
import styled from 'styled-components';
import { darken } from 'polished';
import copy from 'copy-to-clipboard';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogActions from '@material-ui/core/DialogActions';
import Zoom from '@material-ui/core/Zoom';
import Button from '@material-ui/core/Button';

const PrimaryButton = styled(Button)`
  && {
    background: #79b443;
    border-radius: 50px;
    color: white;
    text-transform: none;
    padding: 5px;
    font-family: Lato;
    font-size: 16px;
    font-weight: 700;
    box-shadow: none;

    &:hover {
      background: ${darken(0.1, '#79B443')};
    }

    @media screen and (min-width: 600px) {
      padding: 10px 25px;
    }
  }
`;

const SecondaryButton = styled(PrimaryButton)`
  && {
    background: #161616;

    &:hover {
      background: ${darken(0.1, '#161616')};
    }
  }
`;

const StyledDialogActions = styled(DialogActions)`
  && {
    margin: 8px 20px 20px;
  }
`;


const Modal = ({ open, closeModal, url }) => (
  <Dialog
    {...{ open }}
    onClose={closeModal}
    TransitionComponent={Zoom}
  >
    <DialogTitle>Share</DialogTitle>
    <DialogContent>
      <DialogContentText>
        <span>Link to share: </span>
        <a href={url}>{url}</a>
      </DialogContentText>
    </DialogContent>
    <StyledDialogActions>
      <SecondaryButton onClick={closeModal}>
        Close
      </SecondaryButton>
      <PrimaryButton onClick={() => copy(url)}>
        Copy To Clipboard
      </PrimaryButton>
    </StyledDialogActions>
  </Dialog>
);

export default Modal;


// Modal.propTypes = {
//   closeModal: t.func.isRequired,
//   videoUrl: t.string,
// }


// Modal.defaultProps = {
//   videoUrl: null,
// }
