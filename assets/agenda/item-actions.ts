import {get} from 'lodash';
import {getItemActions} from '../item-actions';
import * as agendaActions from './actions';
import {gettext} from '../utils';
import {isWatched} from './utils';

const canWatchAgendaItem = (state: any, item: any, includeCoverages: any) => {
    const result = state.user && !isWatched(item, state.user);
    if (!state.bookmarks || includeCoverages) {
        return result;
    }

    const coveragesWatched = (get(item, 'coverages') || []).filter((c: any) => isWatched(c, state.user));
    return coveragesWatched.length > 0 ? false : result;
};

export const getAgendaItemActions = (dispatch: any) => {
    const {watchEvents, stopWatchingEvents} = agendaActions;
    return (getItemActions(dispatch, {...agendaActions}) as any).concat([
        {
            name: gettext('Watch'),
            icon: 'watch',
            multi: true,
            when: (state: any, item: any, includeCoverages: any) => canWatchAgendaItem(state, item, includeCoverages),
            action: (items: any) => dispatch(watchEvents(items)),
        },
        {
            name: gettext('Stop watching'),
            icon: 'unwatch',
            multi: true,
            when: (state: any, item: any, includeCoverages: any) => !canWatchAgendaItem(state, item, includeCoverages),
            action: (items: any) => dispatch(stopWatchingEvents(items)),
        },
    ]);
};

export const getCoverageItemActions = (dispatch: any) => {
    const {watchCoverage, stopWatchingCoverage} = agendaActions;
    return [
        {
            name: gettext('Watch'),
            icon: 'watch',
            when: (cov: any, user: any) => user && !isWatched(cov, user),
            action: (coverage: any, group: any, item: any) => dispatch(watchCoverage(coverage, item)),
            tooltip: gettext('Watch this coverage'),
        },
        {
            name: gettext('Stop watching'),
            icon: 'unwatch',
            when: (cov: any, user: any) => user && isWatched(cov, user),
            action: (coverage: any, group: any, item: any) => dispatch(stopWatchingCoverage(coverage, item)),
        },
    ];
};

