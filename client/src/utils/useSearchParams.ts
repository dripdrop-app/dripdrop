import isEqual from "lodash/isEqual";
import { useCallback } from "react";
import { useSearchParams as useRouterSearchParams } from "react-router-dom";

type ParamValue = string | number | string[] | boolean;

type SearchParams = Record<string, ParamValue>;

const convertToSearchParams = <T>(object: Partial<T>) => {
  const searchParams = {} as Record<string, string>;
  for (const key in object) {
    const value = object[key];
    if (typeof value === "string") {
      searchParams[key] = value;
    } else if (typeof value === "number") {
      searchParams[key] = value.toString();
    } else if (typeof value === "boolean") {
      searchParams[key] = value ? "1" : "0";
    } else if (Array.isArray(value)) {
      searchParams[key] = value.join(",");
    }
  }
  return searchParams;
};

const revertSearchParams = <T>(initial: T, params: URLSearchParams) => {
  const object = { ...initial } as T;
  for (const key in initial) {
    const param = params.get(key);
    const initialValue = initial[key];
    if (param) {
      if (typeof initialValue === "string") {
        if (initialValue !== param) {
          (object[key] as string) = param;
        }
      } else if (typeof initialValue === "number") {
        const parsedParam = parseInt(param);
        if (initialValue !== parsedParam) {
          (object[key] as number) = parsedParam;
        }
      } else if (typeof initialValue === "boolean") {
        const parsedParam = parseInt(param) === 1;
        if (initialValue !== parsedParam) {
          (object[key] as boolean) = parsedParam;
        }
      } else if (Array.isArray(initialValue)) {
        const parsedParam = param.split(",");
        if (!isEqual(initialValue, parsedParam)) {
          (object[key] as string[]) = parsedParam;
        }
      }
    }
  }
  return object;
};

const useSearchParams = <T extends SearchParams>(initial: T) => {
  const [routerSearchParams, setRouterSearchParams] = useRouterSearchParams(convertToSearchParams(initial));

  const setSearchParams = useCallback(
    (update: Partial<T>) => {
      setRouterSearchParams((prevSearchParams) => {
        const convertedParams = convertToSearchParams(update);
        for (const key in convertedParams) {
          prevSearchParams.set(key, convertedParams[key]);
        }
        return prevSearchParams;
      });
    },
    [setRouterSearchParams]
  );

  return { params: revertSearchParams(initial, routerSearchParams), setSearchParams };
};

export default useSearchParams;
