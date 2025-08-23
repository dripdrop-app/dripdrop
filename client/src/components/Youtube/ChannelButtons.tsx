import { ActionIcon, Text, Tooltip } from "@mantine/core";
import { openConfirmModal } from "@mantine/modals";
import { FunctionComponent } from "react";
import { MdAddCircle, MdRemoveCircle } from "react-icons/md";

import { useAddYoutubeSubscriptionMutation, useRemoveSubscriptionMutation } from "../../api/youtube";

interface SubscribeButtonProps {
  channelTitle: string;
  channelId: string;
  subscribed: boolean;
}

export const SubscribeButton: FunctionComponent<SubscribeButtonProps> = ({ channelId, channelTitle, subscribed }) => {
  const [addYoutubeSubscription, addYoutubeSubscriptionStatus] = useAddYoutubeSubscriptionMutation();
  const [removeYoutubeSubscription, removeYoutubeSubscriptionStatus] = useRemoveSubscriptionMutation();

  if (!subscribed) {
    return (
      <Tooltip label="Subscribe">
        <ActionIcon
          variant="transparent"
          color="white"
          onClick={() => addYoutubeSubscription(channelId)}
          loading={addYoutubeSubscriptionStatus.isLoading}
        >
          <MdAddCircle size={25} color="green" />
        </ActionIcon>
      </Tooltip>
    );
  }
  return (
    <Tooltip label="Unsubscribe">
      <ActionIcon
        variant="transparent"
        color="white"
        onClick={() =>
          openConfirmModal({
            title: "Confirm Remove Subscription",
            children: (
              <Text>
                Remove subscription from channel:{" "}
                <Text display="inline-block" fw="bold">
                  {channelTitle}
                </Text>
              </Text>
            ),
            labels: { confirm: "Confirm", cancel: "Cancel" },
            onConfirm: () => removeYoutubeSubscription(channelId),
          })
        }
        loading={removeYoutubeSubscriptionStatus.isLoading}
      >
        <MdRemoveCircle size={25} color="red" />
      </ActionIcon>
    </Tooltip>
  );
};
