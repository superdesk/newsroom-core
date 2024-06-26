import React from 'react';
import {connect} from 'react-redux';
import {createSelector} from 'reselect';
import {isEqual, cloneDeep} from 'lodash';
import classNames from 'classnames';
import moment from 'moment';

import {
    IAgendaItem,
    IPlanningItem,
    IAgendaListGroup,
    IAgendaListGroupItem,
    ICompany,
    IItemAction,
    IListConfig,
    IPreviewConfig,
    IUser,
    IUserType,
    IAgendaState,
} from 'interfaces';
import {gettext, DATE_FORMAT, isDisplayed, shouldShowListShortcutActionIcons} from 'utils';

import AgendaListItem from './AgendaListItem';
import {AgendaListGroupHeader} from './AgendaListGroupHeader';

import {setActive, previewItem, toggleSelected, openItem, toggleHiddenGroupItems} from '../actions';
import {EXTENDED_VIEW} from 'wire/defaults';
import {getIntVersion} from 'wire/utils';
import {getPlanningItemsByGroup, getListItems, isTopStory} from 'agenda/utils';
import {searchNavigationSelector} from 'search/selectors';
import {previewConfigSelector, listConfigSelector} from 'ui/selectors';
import {AGENDA_DATE_FORMAT_LONG, AGENDA_DATE_FORMAT_SHORT, AGENDA_TOP_STORY_SORTING_ONLY} from '../../utils';


const PREVIEW_TIMEOUT = 500; // time to preview an item after selecting using kb
const CLICK_TIMEOUT = 200; // time when we wait for double click after click
const EMPTY_OBJECT = {};

const itemsByIdSelector = (state: IAgendaState) => state.itemsById || EMPTY_OBJECT;
const groupedItemsSelector = (state: IAgendaState) => state.listItems.groups;

const hiddenGroupsShownSelector = (state: IAgendaState) => state.listItems.hiddenGroupsShown;

const getItemIdsSorted = (
    itemIds: Array<string>,
    itemsById: {[itemId: string]: IAgendaItem},
    listConfig: IListConfig,
    group: IAgendaListGroup,
) => {
    const topStoryIds: Array<string> = [];
    const coveragesOnlyIds: Array<string> = [];
    const restIds: Array<string> = [];

    itemIds.forEach((id) => {
        const item = itemsById[id];
        const hasCoverage = (item.coverages?.length ?? 0) > 0;
        const topStory = (item.subject ?? []).find(isTopStory);

        if (topStory) {

            // hiddenItems has items which are multiDay and are not on the first date of the group
            if (group.hiddenItems.includes(item._id) === false) {
                topStoryIds.push(item._id);
            } else {
                restIds.push(item._id);
            }
        } else if (hasCoverage && AGENDA_TOP_STORY_SORTING_ONLY == false) {

            // items with coverages are displayed after top stories
            coveragesOnlyIds.push(item._id);
        } else {

            // all other items should follow
            restIds.push(item._id);
        }
    });

    return [
        ...topStoryIds,
        ...coveragesOnlyIds,
        ...restIds,
    ];
};

/**
 * Single event or planning item could be display multiple times.
 * Hence, the list items needs to tbe calculate so that keyboard scroll works.
 * This selector calculates list of items.
 */
const listItemsSelector = createSelector<
    IAgendaState,
    Array<IAgendaListGroup>,
    IAgendaState['itemsById'],
    {[dateString: string]: boolean},
    Array<IAgendaListGroupItem>
>(
    [groupedItemsSelector, itemsByIdSelector, hiddenGroupsShownSelector],
    getListItems
);

interface IStateProps {
    itemsById: {[itemId: string]: IAgendaItem};
    activeItem?: {_id: IAgendaItem['_id'], group: string, plan?: IAgendaItem['_id']};
    previewItemId?: IAgendaItem['_id'];
    previewGroup?: string;
    previewPlan?: IAgendaItem['_id'];
    selectedItems: Array<IAgendaItem['_id']>;
    readItems: {[itemId: string]: number};
    bookmarks: boolean;
    user: IUser['_id'];
    company?: ICompany['_id'];
    groupedItems: Array<IAgendaListGroup>;
    activeDate: number;
    searchInitiated: boolean;
    activeNavigation: Array<string>;
    resultsFiltered: boolean;
    listItems: Array<IAgendaListGroupItem>;
    isLoading: boolean;
    previewConfig: IPreviewConfig;
    featuredOnly: boolean;
    listConfig: IListConfig;
    userType: IUserType;
    hiddenGroupsShown: {[dateString: string]: boolean};
    itemTypeFilter: IAgendaState['agenda']['itemType'];
}

interface IDispatchProps {
    setActive(item?: IAgendaListGroupItem): void;
    previewItem(item?: IAgendaItem, group?: string, planId?: IAgendaItem['_id']): void;
    openItem(item: IAgendaItem, group: string, plan?: IAgendaItem['_id']): void;
    toggleSelected(itemId: IAgendaItem['_id']): void;
    toggleHiddenGroupItems(dateString: string): void;
}

interface IOwnProps {
    actions: Array<IItemAction>;
    activeView: string;
    onScroll(event: React.MouseEvent<HTMLDivElement>): void;
    refNode(element: HTMLDivElement): void;
}

type IProps = IStateProps & IDispatchProps & IOwnProps;

interface IState {
    actioningItem?: IAgendaItem;
    activePlan?: IAgendaItem;
    activeGroup?: string;
}

class AgendaList extends React.Component<IProps, IState> {
    previewTimeout?: number;
    clickTimeout?: number;
    elem?: HTMLDivElement;

    constructor(props: IProps) {
        super(props);

        this.state = {
            actioningItem: undefined,
            activePlan: undefined,
            activeGroup: undefined,
        };

        this.onKeyDown = this.onKeyDown.bind(this);
        this.onItemClick = this.onItemClick.bind(this);
        this.onItemDoubleClick = this.onItemDoubleClick.bind(this);
        this.onActionList = this.onActionList.bind(this);
        this.filterActions = this.filterActions.bind(this);
        this.resetActioningItem = this.resetActioningItem.bind(this);
        this.isActiveItem = this.isActiveItem.bind(this);
    }

    onKeyDown(event: React.KeyboardEvent) {
        let diff = 0;
        switch (event.key) {
        case 'ArrowDown':
            this.setState({actioningItem: undefined});
            diff = 1;
            break;

        case 'ArrowUp':
            this.setState({actioningItem: undefined});
            diff = -1;
            break;

        case 'Escape':
            this.setState({actioningItem: undefined});
            this.props.setActive();
            this.props.previewItem();
            return;

        default:
            return;
        }

        event.preventDefault();
        const activeItem = this.props.activeItem;

        const activeIndex = activeItem == null ?
            -1 :
            this.props.listItems.findIndex((item) => (
                item._id === activeItem._id &&
                item.group === activeItem.group &&
                item.plan === activeItem.plan
            ));

        // keep it within (0, items.length) interval
        const nextIndex = Math.max(0, Math.min(activeIndex + diff, this.props.listItems.length - 1));
        const nextItemInList = this.props.listItems[nextIndex];
        const nextItem = this.props.itemsById[nextItemInList._id];

        this.props.setActive({
            _id: nextItemInList._id,
            group: nextItemInList.group,
            plan: nextItemInList.plan,
        });

        if (this.previewTimeout != null) {
            clearTimeout(this.previewTimeout);
        }

        this.previewTimeout = window.setTimeout(() => {
            this.props.previewItem(nextItem, nextItemInList.group, nextItemInList.plan);
        }, PREVIEW_TIMEOUT);

        const activeElements = document.getElementsByClassName('wire-articles__item--open');

        if (activeElements && activeElements.length) {
            activeElements[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});
        }
    }

    cancelPreviewTimeout() {
        if (this.previewTimeout) {
            clearTimeout(this.previewTimeout);
            this.previewTimeout = undefined;
        }
    }

    cancelClickTimeout() {
        if (this.clickTimeout != null) {
            clearTimeout(this.clickTimeout);
            this.clickTimeout = undefined;
        }
    }

    onItemClick(item: IAgendaItem, group: string, plan?: IAgendaItem['_id']) {
        const itemId = item._id;
        this.setState({actioningItem: undefined});
        this.cancelPreviewTimeout();
        this.cancelClickTimeout();

        this.clickTimeout = window.setTimeout(() => {
            this.props.setActive({_id: itemId, group: group, plan: plan});

            if (this.props.previewItemId !== itemId ||
                this.props.previewGroup !== group ||
                this.props.previewPlan !== plan) {
                this.props.previewItem(item, group, plan);
            } else {
                this.props.previewItem();
            }
        }, CLICK_TIMEOUT);
    }

    resetActioningItem() {
        this.setState({actioningItem: undefined});
    }

    onItemDoubleClick(item: IAgendaItem, group: string, plan?: IAgendaItem['_id']) {
        this.cancelClickTimeout();
        this.props.setActive({_id: item._id, group: group, plan: plan});
        this.props.openItem(item, group, plan);
    }

    onActionList(event: React.MouseEvent, item: IAgendaItem, group: string, plan?: IAgendaItem) {
        event.stopPropagation();
        if (this.state.actioningItem && this.state.actioningItem._id === item._id &&
            (!this.state.activePlan || (this.state.activePlan && this.state.activePlan.guid === plan?.guid))) {
            this.setState({actioningItem: undefined, activeGroup: undefined, activePlan: undefined});
        } else {
            this.setState({actioningItem: item, activeGroup: group, activePlan: plan});
        }
    }

    filterActions(item: IAgendaItem, config: IPreviewConfig) {
        return this.props.actions.filter((action) =>  (!config || isDisplayed(action.id, config)) &&
          (!action.when || action.when(this.props, item)));
    }

    isActiveItem(_id: IAgendaItem['_id'], group: string, plan?: IPlanningItem) {
        const {activeItem} = this.props;

        if (activeItem == null || (!_id && !group && !plan)) {
            return false;
        }

        if (_id && group && plan) {
            return (
                _id === activeItem._id &&
                group === activeItem.group &&
                plan.guid === activeItem.plan
            );
        }

        if (_id && group) {
            return _id === activeItem._id && group === activeItem.group;
        }

        return _id === activeItem._id;
    }

    componentDidUpdate(prevProps: Readonly<IProps>) {
        if (this.elem != null && (
            prevProps.activeDate !== this.props.activeDate ||
            !isEqual(prevProps.activeNavigation, this.props.activeNavigation) ||
            (!prevProps.searchInitiated && this.props.searchInitiated)
        )) {
            this.elem.scrollTop = 0;
        }
    }

    getListGroupDate(group: IAgendaListGroup) {
        if (group.date != null) {
            const groupDate = moment(group.date, DATE_FORMAT);
            const today = moment();
            const tomorrow  = moment(today).add(1,'days');
            if (groupDate.isSame(today, 'day')) {
                return gettext('Today');
            }

            if (groupDate.isSame(tomorrow, 'day')) {
                return gettext('Tomorrow');
            }

            return groupDate.format(groupDate.year() === today.year() ? AGENDA_DATE_FORMAT_SHORT : AGENDA_DATE_FORMAT_LONG);
        }
    }

    renderGroupItems(group: IAgendaListGroup, forHiddenItems: boolean) {
        const itemIds = forHiddenItems === true ? group.hiddenItems : group.items;
        const isExtended = this.props.activeView === EXTENDED_VIEW;
        const showShortcutActionIcons = shouldShowListShortcutActionIcons(this.props.listConfig, isExtended);

        return (
            <div
                className="wire-articles__group"
                key={`${group.date}-${forHiddenItems ? 'hidden-items' : 'items'}-group`}
            >
                {getItemIdsSorted(itemIds, this.props.itemsById, this.props.listConfig, group).map((itemId) => {
                    // Only show multiple entries for this item if we're in the `Planning Only` view
                    const plans = this.props.itemTypeFilter !== 'planning' ?
                        [] :
                        getPlanningItemsByGroup(this.props.itemsById[itemId], group.date);

                    return plans.length > 0 ? (
                        <React.Fragment key={`${itemId}--${group.date}`}>
                            {plans.map((plan) => (
                                <AgendaListItem
                                    key={`${itemId}--${plan._id}`}
                                    group={group.date}
                                    item={cloneDeep(this.props.itemsById[itemId])}
                                    isActive={this.isActiveItem(itemId, group.date, plan)}
                                    isSelected={this.props.selectedItems.includes(itemId)}
                                    isRead={this.props.readItems[itemId] === getIntVersion(this.props.itemsById[itemId])}
                                    onClick={this.onItemClick}
                                    onDoubleClick={this.onItemDoubleClick}
                                    onActionList={this.onActionList}
                                    showActions={this.state.actioningItem != null &&
                                        this.state.actioningItem._id === itemId &&
                                        group.date === this.state.activeGroup &&
                                        plan.guid === this.state.activePlan?.guid
                                    }
                                    toggleSelected={() => this.props.toggleSelected(itemId)}
                                    actions={this.filterActions(this.props.itemsById[itemId], this.props.previewConfig)}
                                    isExtended={isExtended}
                                    user={this.props.user}
                                    actioningItem={this.state.actioningItem}
                                    planningId={plan.guid}
                                    resetActioningItem={this.resetActioningItem}
                                    showShortcutActionIcons={showShortcutActionIcons}
                                    listConfig={this.props.listConfig}
                                />
                            ))}
                        </React.Fragment>
                    ) : (
                        <AgendaListItem
                            key={itemId}
                            group={group.date}
                            item={this.props.itemsById[itemId]}
                            isActive={this.isActiveItem(itemId, group.date, undefined)}
                            isSelected={this.props.selectedItems.includes(itemId)}
                            isRead={this.props.readItems[itemId] === getIntVersion(this.props.itemsById[itemId])}
                            onClick={this.onItemClick}
                            onDoubleClick={this.onItemDoubleClick}
                            onActionList={this.onActionList}
                            showActions={this.state.actioningItem != null &&
                                this.state.actioningItem._id === itemId &&
                                group.date === this.state.activeGroup
                            }
                            toggleSelected={() => this.props.toggleSelected(itemId)}
                            actions={this.filterActions(this.props.itemsById[itemId], this.props.previewConfig)}
                            isExtended={isExtended}
                            user={this.props.user}
                            actioningItem={this.state.actioningItem}
                            resetActioningItem={this.resetActioningItem}
                            showShortcutActionIcons={showShortcutActionIcons}
                            listConfig={this.props.listConfig}
                        />
                    );
                })}
            </div>
        );
    }

    render() {
        const lastGroupWithItems = getLastGroupWithItems(this.props.groupedItems);
        const groupedItems = this.props.groupedItems.slice(0, lastGroupWithItems + 1);

        return (
            <div
                className={classNames('wire-articles wire-articles--list', {
                    'wire-articles--list-compact': this.props.activeView !== EXTENDED_VIEW,
                })}
                onKeyDown={this.onKeyDown}
                ref={(elem) => {
                    if (elem != null) {
                        this.props.refNode(elem);
                        this.elem = elem;
                    }
                }}
                onScroll={this.props.onScroll}
            >
                {groupedItems.length === 1 ?
                    this.renderGroupItems(groupedItems[0], false) :
                    groupedItems.map((group) => (
                        <React.Fragment key={group.date}>
                            <div className='wire-articles__header' key={`${group.date}header`}>
                                {this.getListGroupDate(group)}
                            </div>

                            {group.hiddenItems.length === 0 ? null : (
                                <AgendaListGroupHeader
                                    group={group.date}
                                    itemIds={group.hiddenItems}
                                    itemsById={this.props.itemsById}
                                    itemsShown={this.props.hiddenGroupsShown[group.date] === true}
                                    toggleHideItems={this.props.toggleHiddenGroupItems}
                                />
                            )}

                            {this.props.hiddenGroupsShown[group.date] !== true ?
                                null :
                                this.renderGroupItems(group, true)
                            }
                            {this.renderGroupItems(group, false)}
                        </React.Fragment>
                    ))
                }
                {!groupedItems.length &&
                    <div className="wire-articles__item-wrap col-12">
                        <div className="alert alert-secondary">{gettext('No items found.')}</div>
                    </div>
                }
            </div>
        );
    }
}

const mapStateToProps = (state: IAgendaState): IStateProps => ({
    itemsById: state.itemsById,
    activeItem: state.activeItem,
    previewItemId: state.previewItem,
    previewGroup: state.previewGroup,
    previewPlan: state.previewPlan,
    selectedItems: state.selectedItems,
    readItems: state.readItems,
    bookmarks: state.bookmarks,
    user: state.user,
    company: state.company,
    groupedItems: groupedItemsSelector(state),
    activeDate: state.agenda.activeDate,
    searchInitiated: state.searchInitiated,
    activeNavigation: searchNavigationSelector(state),
    resultsFiltered: state.resultsFiltered,
    listItems: listItemsSelector(state),
    isLoading: state.isLoading,
    previewConfig: previewConfigSelector(state),
    featuredOnly: state.agenda.featuredOnly,
    listConfig: listConfigSelector(state),
    userType: state.userType,
    hiddenGroupsShown: hiddenGroupsShownSelector(state),
    itemTypeFilter: state.agenda?.itemType,
});

const mapDispatchToProps: IDispatchProps = {
    setActive,
    previewItem,
    openItem,
    toggleSelected,
    toggleHiddenGroupItems,
};

const component = connect<
    IStateProps,
    IDispatchProps,
    IOwnProps,
    IAgendaState
>(mapStateToProps, mapDispatchToProps)(AgendaList);

export default component;

function getLastGroupWithItems(groupedItems: Array<IAgendaListGroup>): number {
    const groupsWithItems = groupedItems.filter((group) => group.items.length > 0);

    if (groupsWithItems.length > 0) {
        const lastGroup = groupsWithItems[groupsWithItems.length - 1];
        return groupedItems.indexOf(lastGroup);
    }

    // If no groups have items, return the last group
    return groupedItems.length - 1;
}
