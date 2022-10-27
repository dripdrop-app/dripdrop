import { configureStore } from '@reduxjs/toolkit';
import baseApi from './api';
import { youtubeSlice } from './state/youtube';

declare global {
	type RootState = ReturnType<typeof store.getState>;
}

export const store = configureStore({
	reducer: {
		[baseApi.reducerPath]: baseApi.reducer,
		[youtubeSlice.name]: youtubeSlice.reducer,
	},
	middleware: (getDefaultMiddleware) =>
		getDefaultMiddleware({
			serializableCheck: false,
		}).concat(baseApi.middleware),
});
