import type { Reducer } from "react";
import { useCallback, useReducer } from "react";

interface Payload<T> {
  object: Partial<T>;
}

interface UpdateAction<T> {
  type: "Update";
  payload: Payload<T>;
}

interface ResetAction {
  type: "Reset";
}

type Action<T> = ResetAction | UpdateAction<T>;

const reducer = <T>(state: T, action: Action<T>) => {
  if (action.type === "Update") {
    const { payload } = action;
    return { ...state, ...payload.object };
  }
  return state;
};

const useObject = <T>(object: T) => {
  const [objectState, dispatch] = useReducer<Reducer<T, Action<T>>>(reducer, object);

  const setObject = useCallback(
    (newObject: Partial<T>) => dispatch({ type: "Update", payload: { object: newObject } }),
    [dispatch]
  );

  return {
    object: objectState,
    setObject,
  };
};

export default useObject;
