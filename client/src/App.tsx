import { AppShell, Avatar, Burger, Center, Flex, Loader, MantineProvider, NavLink, Title } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { ModalsProvider } from "@mantine/modals";
import { Notifications } from "@mantine/notifications";
import { useEffect } from "react";
import { BsYoutube } from "react-icons/bs";
import { MdAccountCircle, MdCloudDownload, MdSubscriptions } from "react-icons/md";
import { Link, matchPath, Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";

import { Account, CreateAccount, Login, PrivacyPolicy, TermsOfService, VerifyAccount } from "./pages/Auth";

import { useCheckSessionQuery } from "./api/auth";
import { MusicDownloader } from "./pages/Music";
import { YoutubeChannel, YoutubeSubscriptions, YoutubeVideo, YoutubeVideos } from "./pages/Youtube";
import { useFooter } from "./providers/FooterProvider";
import { useOverlay } from "./providers/OverlayProvider";

const AuthenticatedRoute = () => {
  const sessionStatus = useCheckSessionQuery();

  const location = useLocation();

  return (
    <>
      {sessionStatus.isFetching && (
        <Center>
          <Loader />
        </Center>
      )}
      {sessionStatus.isSuccess && <Outlet />}
      {sessionStatus.isError && <Navigate to="/login" state={{ next: location }} />}
    </>
  );
};

const App = () => {
  const [openedSideBar, handlers] = useDisclosure(false);
  const sessionStatus = useCheckSessionQuery();
  const location = useLocation();
  const { displayFooter, footerRef } = useFooter();
  const { overlayRef } = useOverlay();

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [location]);

  return (
    <MantineProvider
      defaultColorScheme="dark"
      theme={{
        breakpoints: {
          xl: "2000",
        },
        components: {
          Anchor: {
            defaultProps: {
              target: "_blank",
              rel: "noopener noreferrer",
            },
          },
          Flex: {
            defaultProps: {
              wrap: { base: "wrap", sm: "nowrap" },
              gap: "md",
            },
          },
          Tooltip: {
            defaultProps: {
              events: { hover: true, focus: false, touch: true },
            },
          },
        },
      }}
    >
      <ModalsProvider>
        <Notifications />
        <AppShell
          padding="md"
          header={{ height: 60 }}
          footer={{ height: displayFooter ? 100 : 0 }}
          navbar={{
            width: 200,
            breakpoint: "sm",
            collapsed: { desktop: false, mobile: !openedSideBar },
          }}
        >
          <AppShell.Header bg="blue.8">
            <Flex align="center" direction="row" h="100%" mx="lg">
              <Burger hiddenFrom="sm" opened={sessionStatus.isSuccess && openedSideBar} onClick={handlers.toggle} />
              <Avatar alt="dripdrop" src="https://dripdrop-prod.nyc3.cdn.digitaloceanspaces.com/assets/dripdrop.png" />
              <Title c="white" order={3} fw={600}>
                dripdrop
              </Title>
            </Flex>
          </AppShell.Header>
          {sessionStatus.isSuccess && (
            <AppShell.Navbar p="sm" zIndex={101}>
              <AppShell.Section grow>
                <NavLink
                  component={Link}
                  to="/music/downloader"
                  label="Music Downloader"
                  onClick={handlers.close}
                  leftSection={<MdCloudDownload />}
                  active={!!matchPath("/music/downloader", location.pathname)}
                />
                <NavLink
                  component={Link}
                  to="/youtube/videos"
                  label="Videos"
                  onClick={handlers.close}
                  leftSection={<BsYoutube />}
                  active={!!matchPath("/youtube/videos", location.pathname)}
                />
                <NavLink
                  component={Link}
                  to="/youtube/subscriptions"
                  label="Subscriptions"
                  onClick={handlers.close}
                  leftSection={<MdSubscriptions />}
                  active={!!matchPath("/youtube/subscriptions", location.pathname)}
                />
              </AppShell.Section>
              <AppShell.Section>
                <NavLink
                  component={Link}
                  to="/account"
                  label="Account"
                  onClick={handlers.close}
                  leftSection={<MdAccountCircle />}
                  active={!!matchPath("/account", location.pathname)}
                />
              </AppShell.Section>
            </AppShell.Navbar>
          )}
          <AppShell.Main>
            <Routes>
              <Route path="/privacy" element={<PrivacyPolicy />} />
              <Route path="/terms" element={<TermsOfService />} />
              <Route path="/create" element={<CreateAccount />} />
              <Route path="/verify" element={<VerifyAccount />} />
              <Route path="/login" element={<Login />} />
              <Route path="/" element={<AuthenticatedRoute />}>
                <Route path="youtube/channel/:id" element={<YoutubeChannel />} />
                <Route path="youtube/subscriptions" element={<YoutubeSubscriptions />} />
                <Route path="youtube/videos" element={<YoutubeVideos />} />
                <Route path="youtube/video/:id" element={<YoutubeVideo />} />
                <Route path="music/downloader" element={<MusicDownloader />} />
                <Route path="account" element={<Account />} />
                <Route path="" element={<Navigate to="music/downloader" replace />} />
              </Route>
              <Route path="*" element={<Navigate to="music/downloader" replace />} />
            </Routes>
          </AppShell.Main>
          <AppShell.Footer display={displayFooter ? "block" : "none"} ref={footerRef}></AppShell.Footer>
          <div ref={overlayRef}></div>
        </AppShell>
      </ModalsProvider>
    </MantineProvider>
  );
};

export default App;
