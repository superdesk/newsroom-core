import {ITopic, ITopicFolder, IUser} from 'interfaces';

import {gettext, notify, errorHandler} from 'utils';
import server from 'server';
import {renderModal, closeModal} from 'actions';
import {store as userProfileStore} from './store';
import {getLocale} from '../utils';
import {reloadMyTopics as reloadMyAgendaTopics} from '../agenda/actions';
import {reloadMyTopics as reloadMyWireTopics} from '../wire/actions';

export const GET_TOPICS = 'GET_TOPICS';
export function getTopics(topics: any) {
    return {type: GET_TOPICS, topics};
}

export const GET_USER = 'GET_USER';
export function getUser(user: any) {
    return {type: GET_USER, user};
}

export const EDIT_USER = 'EDIT_USER';
export function editUser(event: any) {
    return {type: EDIT_USER, event};
}

export const INIT_DATA = 'INIT_DATA';
export function initData(data: any) {
    return {type: INIT_DATA, data};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors: any) {
    return {type: SET_ERROR, errors};
}

export const SELECT_MENU = 'SELECT_MENU';
export function selectMenu(data: any): any {
    return function(dispatch: any) {
        dispatch({type: SELECT_MENU, data});
        dispatch(reloadMyTopics());
    };
}

export const SET_TOPIC_EDITOR_FULLSCREEN = 'SET_TOPIC_EDITOR_FULLSCREEN';
export function setTopicEditorFullscreen(fullscreen: any) {
    return {type: SET_TOPIC_EDITOR_FULLSCREEN, payload: fullscreen};
}

export const SELECT_MENU_ITEM = 'SELECT_MENU_ITEM';
export function selectMenuItem(item: any) {
    return {type: SELECT_MENU_ITEM, item};
}

export function createOrUpdateTopic(menu: any, item: any, fullscreen: any) {
    userProfileStore.dispatch(selectMenuItem(item));
    userProfileStore.dispatch(selectMenu(menu));
    userProfileStore.dispatch(setTopicEditorFullscreen(fullscreen));
}

export const SELECT_PROFILE_MENU = 'SELECT_PROFILE_MENU';
export function selectProfileMenu({menu, item}: any) {
    userProfileStore.dispatch({
        type: SELECT_PROFILE_MENU,
        menu: menu,
        item: item,
    });
}

export const TOGGLE_DROPDOWN = 'TOGGLE_DROPDOWN';
export function toggleDropdown() {
    return {type: TOGGLE_DROPDOWN};
}

export const HIDE_MODAL = 'HIDE_MODAL';
export function hideModal() {
    return {type: HIDE_MODAL};
}


/**
 * Fetches user details
 */
export function fetchUser(id: any) {
    return function (dispatch: any) {
        return server.get(`/users/${id}`)
            .then((data: any) => {
                dispatch(getUser(data));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Saves a user
 *
 */
export function saveUser() {
    return function (dispatch: any, getState: any) {

        const editedUser: any = {...getState().editedUser};
        const url = `/users/${editedUser._id}/profile`;

        // Remove ``sections`` and ``products`` as these aren't managed in the ``UserProfile`` app
        delete editedUser.sections;
        delete editedUser.products;

        return server.post(url, editedUser)
            .then(function() {
                notify.success(gettext('User updated successfully'));
                dispatch(fetchUser(editedUser._id));
                if (editedUser.locale && getLocale() !== editedUser.locale) {
                    notify.warning(
                        gettext(
                            'Please reload the page in order to change language.'
                        )
                    );
                }
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));

    };
}

/**
 * Fetches followed topics for the user
 *
 */
export function fetchTopics() {
    return function (dispatch: any, getState: any) {
        return server.get(`/users/${getState().user._id}/topics`)
            .then((data: any) => {
                return dispatch(getTopics(data._items));
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Deletes the given followed topic
 *
 */
export function deleteTopic(topic: any) {
    return function (dispatch: any) {
        const url = `/topics/${topic._id}`;
        return (server as any).del(url)
            .then(() => {
                notify.success(gettext('Topic deleted successfully'));
                dispatch(fetchTopics());
            })
            .catch((error: any) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Start share followed topic - display modal to pick users
 *
 * @return {function}
 */
export function shareTopic(items: any) {
    return (dispatch: any, getState: any) => {
        const user = getState().user;
        const company = getState().company;
        return server.get(`/companies/${company}/users`)
            .then((users: any) => users.filter((u: any) => u._id !== user._id))
            .then((users: any) => dispatch(renderModal('shareItem', {items, users})))
            .catch(errorHandler);
    };
}

export function openEditTopicNotificationsModal() {
    return (dispatch: any, getState: any) => {
        const user = getState().user;

        dispatch(renderModal('editNotificationSchedule', {user}));
    };
}

/**
 * Submit share followed topic form and close modal if that works
 *
 * @param {Object} data
 */
export function submitShareTopic(data: any) {
    return (dispatch: any) => {
        return server.post('/topic_share', data)
            .then(() => {
                notify.success(gettext('Topic was shared successfully.'));
                dispatch(closeModal());
            })
            .catch(errorHandler);
    };
}


/**
 * Updates a followed topic
 *
 */
export function submitFollowTopic(topic: any) {
    return (dispatch: any) => {
        const url = `/topics/${topic._id}`;
        return server.post(url, topic)
            .then(() => dispatch(fetchTopics()))
            .then(() => dispatch(closeModal()))
            .catch(errorHandler);
    };
}

function reloadMyTopics() {
    return function(dispatch: any, getState: any) {
        const reloadMyTopicsFunction = getState().selectedMenu === 'events' ? reloadMyAgendaTopics : reloadMyWireTopics;

        return dispatch(reloadMyTopicsFunction());
    };
}

export function pushNotification(push: any): any {
    return (dispatch: any, getState: any) => {
        const user = getState().user;
        const company = getState().company;
        const shouldReloadTopics = [
            `topics:${user}`,
            `topics:company-${company}`,
            `topic_created:${user}`,
            `topic_created:company-${company}`,
        ].includes(push.event);

        if (shouldReloadTopics) {
            return dispatch(reloadMyTopics());
        }
    };
}

function getFoldersUrl(state: any, global: boolean | undefined, id?: any) {
    const baseUrl = global ?
        `/api/companies/${state.company}/topic_folders` :
        `/api/users/${state.user._id}/topic_folders`;

    return id != null ? `${baseUrl}/${id}` : baseUrl;
}

function mergeUpdates(updates: any, response: any) {
    updates._id = response._id;
    updates._etag = response._etag;
    updates._status = response._status;
    updates._updated = response._updated;
}

export const FOLDER_UPDATED = 'FOLDER_UPDATED';
export function saveFolder(folder: ITopicFolder, data: {name: string}, global?: boolean) {
    return (dispatch: any, getState: any) => {
        const state = getState();
        const url = getFoldersUrl(state, global, folder._id);

        if (folder._etag) {
            const updates = {...data};

            return server.patch(url, updates, folder._etag)
                .then(() => {
                    dispatch(fetchFolders());
                });
        } else {
            const payload = {...data, section: state.selectedMenu === 'events' ? 'agenda' : 'wire'};

            return server.post(url, payload)
                .then(() => {
                    dispatch(fetchFolders());
                });
        }
    };
}

export const FOLDER_DELETED = 'FOLDER_DELETED';
export function deleteFolder(folder: any, global: boolean, deleteTopics?: boolean) {

    return (dispatch: any, getState: any) => {
        const state = getState();
        const url = getFoldersUrl(state, global, folder._id);

        if (!window.confirm(gettext('Are you sure you want to delete the folder {{name}} and all of its contents?', {name: folder.name}))) {
            return;
        }

        return server.del(url, {topics: deleteTopics}, folder._etag)
            .then(() => dispatch({type: FOLDER_DELETED, payload: {folder}}));
    };
}

export const RECIEVE_FOLDERS = 'RECIEVE_FOLDERS';

/**
 * @param {bool} global - fetch company or user folders
 * @param {bool} skipDispatch - if true it won't replace folders in store
 */
export function fetchFolders() {
    return (dispatch: any, getState: any) => {
        const state = getState();
        const companyTopicsUrl = getFoldersUrl(state, true);
        const userTopicsUrl = getFoldersUrl(state, false);

        return Promise.all([
            state.company !== 'None' ? server.get(companyTopicsUrl).then(({_items}: {_items: Array<any>}) => _items) : Promise.resolve([]),
            server.get(userTopicsUrl).then(({_items}: {_items: Array<any>}) => _items),
        ]).then(([companyFolders, userFolders]) => {
            dispatch({
                type: RECIEVE_FOLDERS,
                payload: {
                    companyFolders: companyFolders,
                    userFolders: userFolders,
                },
            });
        }).catch((error) => {
            console.error(error);
            return Promise.reject();
        });
    };
}

export const TOPIC_UPDATED = 'TOPIC_UPDATED';
export function moveTopic(topicId: any, folder: any) {
    return (dispatch: any, getState: any) => {
        const state = getState();
        const updates = {folder: folder != null ? folder._id : null};
        const topic = state.topics.find((topic: any) => topic._id === topicId);

        return updateTopic(topic, updates, dispatch);
    };
}

export function updateUserNotificationSchedules(schedule: Omit<IUser['notification_schedule'], 'last_run_time'>) {
    return (dispatch: any, getState: any) => {
        const user = getState().user;

        return server.post(`/users/${user._id}/notification_schedules`, schedule)
            .then(() => {
                notify.success(gettext('Global schedule updated'));
                dispatch(fetchUser(user._id));
                dispatch(closeModal());
            })
            .catch((error) => errorHandler(error, dispatch, setError(error)));
    };
}

export function setTopicSubscribers(topic: ITopic, subscribers: ITopic['subscribers']) {
    return (dispatch: any, getState: any) => {
        const user = getState().user;
        const updates = {subscribers};
        return updateTopic(topic, updates, dispatch).then(() => {
            // refresh user profile after topics change
            // to get notifications updates
            dispatch(fetchUser(user._id));
        });
    };
}

function updateTopic(topic: ITopic, updates: Partial<ITopic>, dispatch: any) {
    const url = `/api/users/${topic.user}/topics/${topic._id}`;

    return server.patch(url, updates, topic._etag).then((response) => {
        mergeUpdates(updates, response);
        dispatch({type: TOPIC_UPDATED, payload: {topic, updates}});
    });
}
