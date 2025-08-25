import {
  Anchor,
  Box,
  Button,
  Flex,
  LoadingOverlay,
  Modal,
  PasswordInput,
  Stack,
  Stepper,
  TextInput,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useCallback, useEffect, useState } from "react";
import { Controller, useForm } from "react-hook-form";

import { useResetPasswordMutation, useSendResetEmailMutation } from "../../api/auth";
import AlertConfirmation from "../AlertConfirmation";

interface SendResetForm {
  email: string;
}

interface ResetPasswordForm {
  token: string;
  password: string;
}

const ForgotPasswordModal = () => {
  const [active, setActive] = useState(0);

  const [opened, handlers] = useDisclosure(false);

  const [sendResetEmail, sendResetEmailStatus] = useSendResetEmailMutation();
  const [resetPassword, resetPasswordStatus] = useResetPasswordMutation();

  const {
    control: sendResetControl,
    reset: sendResetFormReset,
    handleSubmit: sendResetSubmit,
  } = useForm<SendResetForm>({
    reValidateMode: "onSubmit",
  });
  const {
    control: resetPasswordControl,
    reset: resetPasswordFormReset,
    handleSubmit: resetPasswordSubmit,
  } = useForm<ResetPasswordForm>({
    reValidateMode: "onSubmit",
  });

  const onSendReset = useCallback((data: SendResetForm) => sendResetEmail(data), [sendResetEmail]);
  const onResetPassword = useCallback((data: ResetPasswordForm) => resetPassword(data), [resetPassword]);

  useEffect(() => {
    if (sendResetEmailStatus.isSuccess) {
      setActive(1);
    }
  }, [sendResetEmailStatus.isSuccess]);

  useEffect(() => {
    sendResetFormReset();
    resetPasswordFormReset();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active]);

  return (
    <>
      <Anchor onClick={handlers.open}>Reset Password</Anchor>
      <Modal size="lg" opened={opened} onClose={handlers.close} closeOnClickOutside={false}>
        <Stepper active={active} onStepClick={setActive}>
          <Stepper.Step label="Send Reset Email">
            <LoadingOverlay visible={sendResetEmailStatus.isLoading} />
            <Box component="form" onSubmit={sendResetSubmit(onSendReset)}>
              <Stack>
                <Controller
                  key="email"
                  name="email"
                  control={sendResetControl}
                  defaultValue={""}
                  rules={{ required: true }}
                  render={({ field, fieldState }) => (
                    <TextInput
                      {...field}
                      label="Email"
                      placeholder="Enter Email"
                      error={fieldState.error?.type === "required" ? "Required" : ""}
                      required
                      withAsterisk
                    />
                  )}
                />
                <AlertConfirmation
                  showError={sendResetEmailStatus.isError}
                  errorMessage={String(sendResetEmailStatus.error)}
                  showSuccess={sendResetEmailStatus.isSuccess}
                  successMessage="Reset password code sent to email"
                />
                <Flex gap="md">
                  <Button type="submit">Submit</Button>
                </Flex>
              </Stack>
            </Box>
          </Stepper.Step>
          <Stepper.Step label="Reset Password">
            <LoadingOverlay visible={resetPasswordStatus.isLoading} />
            <Box component="form" onSubmit={resetPasswordSubmit(onResetPassword)}>
              <Stack>
                <Controller
                  key="token"
                  name="token"
                  control={resetPasswordControl}
                  defaultValue={""}
                  rules={{ required: true }}
                  render={({ field, fieldState }) => (
                    <TextInput
                      {...field}
                      label="Token"
                      placeholder="Enter Token"
                      error={fieldState.error?.type === "required" ? "Required" : ""}
                      required
                      withAsterisk
                    />
                  )}
                />
                <Controller
                  key="password"
                  name="password"
                  control={resetPasswordControl}
                  defaultValue={""}
                  rules={{ required: true }}
                  render={({ field, fieldState }) => (
                    <PasswordInput
                      {...field}
                      label="New Password"
                      placeholder="Enter New Password"
                      error={fieldState.error?.type === "required" ? "Required" : ""}
                      required
                      withAsterisk
                    />
                  )}
                />
                <AlertConfirmation
                  showError={resetPasswordStatus.isError}
                  errorMessage={String(resetPasswordStatus.error)}
                  showSuccess={resetPasswordStatus.isSuccess}
                  successMessage="Password reset Successfully !"
                />
                <Flex gap="md">
                  <Button type="submit">Submit</Button>
                </Flex>
              </Stack>
            </Box>
          </Stepper.Step>
        </Stepper>
      </Modal>
    </>
  );
};

export default ForgotPasswordModal;
