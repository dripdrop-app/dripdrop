import { FetchBaseQueryError } from "@reduxjs/toolkit/query";

const isErrorWithMessage = (error: any): error is { detail: string } =>
  typeof error === "object" && error != null && "detail" in error && typeof (error as any).detail === "string";

export const transformErrorResponse = (response: FetchBaseQueryError) => {
  if (isErrorWithMessage(response.data)) {
    return response.data.detail;
  }
  return response.data;
};
