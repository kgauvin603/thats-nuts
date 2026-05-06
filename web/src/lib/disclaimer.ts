import {
  SAFETY_DISCLAIMER_VERSION,
  SAFETY_STORAGE_KEY,
} from './constants';

export function hasAcceptedDisclaimer(storage: Storage = window.localStorage) {
  return storage.getItem(SAFETY_STORAGE_KEY) === SAFETY_DISCLAIMER_VERSION;
}

export function acceptDisclaimer(storage: Storage = window.localStorage) {
  storage.setItem(SAFETY_STORAGE_KEY, SAFETY_DISCLAIMER_VERSION);
}
