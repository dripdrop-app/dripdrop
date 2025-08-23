import { Alert } from "@mantine/core";
import { FunctionComponent } from "react";
import { MdCheck, MdError } from "react-icons/md";

interface AlertConfirmationProps {
  showSuccess?: boolean;
  successMessage?: string;
  showError?: boolean;
  errorMessage?: string;
}

const AlertConfirmation: FunctionComponent<AlertConfirmationProps> = ({
  showSuccess,
  successMessage,
  showError,
  errorMessage,
}) => {
  return (
    <>
      <Alert style={{ ...(!showSuccess && { display: "none" }) }} icon={<MdCheck />} title="Success" color="green">
        {successMessage}
      </Alert>
      <Alert style={{ ...(!showError && { display: "none" }) }} icon={<MdError />} title="Error" color="red">
        {errorMessage}
      </Alert>
    </>
  );
};

export default AlertConfirmation;
