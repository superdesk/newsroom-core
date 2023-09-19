import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {get, isEqual} from 'lodash';

import ActionButton from 'components/ActionButton';

import AgendaListItemIcons from './AgendaListItemIcons';
import AgendaItemTimeUpdater from './AgendaItemTimeUpdater';
import AgendaInternalNote from './AgendaInternalNote';
import {PlainText} from 'ui/components/PlainText';

import {
    hasCoverages,
    isCanceled,
    isPostponed,
    isRescheduled,
    getName,
    isWatched,
    getDescription,
    getHighlightedDescription,
    getHighlightedName,
    getInternalNote,
} from '../utils';
import ActionMenu from '../../components/ActionMenu';
import {LIST_ANIMATIONS, isMobilePhone} from 'utils';

class AgendaListItem extends React.Component<any, any> {
    static propTypes: any;

    slugline: any;
    state: any;
    dom: any;

    constructor(props: any) {
        super(props);
        this.slugline = props.item.slugline && props.item.slugline.trim();

        this.state = {previousVersions: false};
        this.dom = {article: null};

        this.onKeyDown = this.onKeyDown.bind(this);
        this.setArticleRef = this.setArticleRef.bind(this);
        this.onArticleClick = this.onArticleClick.bind(this);
        this.onArticleDoubleClick = this.onArticleDoubleClick.bind(this);
        this.onMouseEnter = this.onMouseEnter.bind(this);
    }

    onKeyDown(event: any) {
        switch (event.key) {
        case ' ':  // on space toggle selected item
            this.props.toggleSelected();
            break;

        default:
            return;
        }

        event.preventDefault();
    }

    setArticleRef(elem: any) {
        this.dom.article = elem;
    }

    onArticleClick() {
        this.props.onClick(this.props.item, this.props.group, this.props.planningId);
    }

    onArticleDoubleClick() {
        this.props.onDoubleClick(this.props.item, this.props.group, this.props.planningId);
    }

    onMouseEnter() {
        if (this.props.actioningItem && this.props.actioningItem._id !== this.props.item._id) {
            this.props.resetActioningItem();
        }
    }

    shouldComponentUpdate(nextProps: any, nextState: any) {
        const {props, state} = this;

        return props.item._etag !== nextProps.item._etag || state.hover !== nextState.hover ||
            props.isActive !== nextProps.isActive || props.isSelected !== nextProps.isSelected ||
            props.isExtended !== nextProps.isExtended ||
            get(props.actioningItem, '_id') === props.item._id ||
            get(nextProps.actioningItem, '_id') === props.item._id ||
            props.isRead !== nextProps.isRead ||
            (get(props, 'item.bookmarks') || []).includes(props.user) !==
            (get(nextProps, 'item.bookmarks') || []).includes(nextProps.user) ||
            isWatched(props.item, props.user) !== isWatched(nextProps.item, nextProps.user) ||
            isEqual(get(nextProps, 'coverages'), get(this.props, 'coverages'));
    }

    componentDidMount() {
        if (this.props.isActive && this.dom.article) {
            this.dom.article.focus();
        }
    }

    stopPropagation(event: any) {
        event.stopPropagation();
    }

    getClassNames(isExtended: any) {
        return {
            card: classNames('wire-articles__item-wrap col-12 agenda-item'),
            wrap: classNames('wire-articles__item wire-articles__item--agenda wire-articles__item--list', {
                'wire-articles__item--covering': hasCoverages(this.props.item),
                'wire-articles__item--watched': isWatched(this.props.item, this.props.user),
                'wire-articles__item--not-covering': !hasCoverages(this.props.item),
                'wire-articles__item--postponed': isPostponed(this.props.item),
                'wire-articles__item--canceled': isCanceled(this.props.item),
                'wire-articles__item--visited': this.props.isRead,
                'wire-articles__item--rescheduled': isRescheduled(this.props.item),
                'wire-articles__item--selected': this.props.isSelected,
                'wire-articles__item--open': this.props.isActive,
            }),
            select: classNames('no-bindable-select', {
                'wire-articles__item-select--visible': !LIST_ANIMATIONS,
                'wire-articles__item-select': LIST_ANIMATIONS,
            }),
            article: classNames('wire-articles__item-text-block', {
                'flex-column align-items-start': !isExtended
            }),
        };
    }

    renderListItem(isMobile: any, children: any) {
        const {item, isExtended, group, planningId, listConfig} = this.props;
        const classes = this.getClassNames(isExtended);
        const planningItem = (get(item, 'planning_items') || []).find((p: any) => p.guid === planningId) || null;
        const description = item.es_highlight
            ? getHighlightedDescription(item, planningItem)
            : getDescription(item,planningItem);
        // Show headline for adhoc planning items
        const showHeadline = !item.event && get(item, 'headline.length', 0) > 0;

        return (
            <article key={item._id}
                className={classes.card}
                ref={this.setArticleRef}
                onClick={this.onArticleClick}
                onDoubleClick={this.onArticleDoubleClick}
                onMouseEnter={this.onMouseEnter}
                onKeyDown={this.onKeyDown}
            >
                <div className={classes.wrap} tabIndex={0}>
                    <div className={classes.article} key="article">
                        <h4 className='wire-articles__item-headline'>
                            <div className={classes.select} onClick={this.stopPropagation}>
                                <label className="circle-checkbox">
                                    <input type="checkbox" className="css-checkbox" checked={this.props.isSelected} onChange={this.props.toggleSelected} />
                                    <i></i>
                                </label>
                            </div>

                            <span className={
                                classNames({'wire-articles__item__meta-time': showHeadline})}>
                                {item.es_highlight ?  <div
                                    dangerouslySetInnerHTML={({__html: getHighlightedName(item)})}/> : getName(item)}</span>
                            {showHeadline && <span
                                className='wire-articles__item__text wire-articles__item__text--large wire-articles__item__text--headline'>
                                {item.es_highlight && item.es_highlight.headline ? <div
                                    dangerouslySetInnerHTML={({__html: item.es_highlight.headline && item.es_highlight.headline[0]})}
                                /> : item.headline}</span>}
                        </h4>

                        {!isMobile ? null : (
                            <AgendaItemTimeUpdater
                                item={item}
                                borderRight={false}
                                alignCenter={false}
                            />
                        )}

                        <AgendaListItemIcons
                            item={item}
                            group={group}
                            planningItem={planningItem}
                            isMobilePhone={isMobile}
                            user={this.props.user}
                            listConfig={listConfig}
                        />

                        {(isMobile || isExtended) && description && (
                            <div className="wire-articles__item__text">
                                {item.es_highlight && item.es_highlight
                                    ? (
                                        description.split('\n').map((lineOfHTML: string, index: number) => {
                                            return (
                                                <p key={index}>
                                                    <span dangerouslySetInnerHTML={{__html: lineOfHTML}} />
                                                </p>
                                            );
                                        })
                                    )
                                    : <PlainText text={description.split('\n')[0]} />
                                }
                            </div>
                        )}
                    </div>
                    {children}
                </div>
            </article>
        );
    }

    renderNonMobile() {
        const {item, planningId} = this.props;
        const planningItem = (get(item, 'planning_items') || []).find((p: any) => p.guid === planningId) || {};

        return this.renderListItem(false, !this.props.actions.length ? null : (
            <div className='wire-articles__item-actions' onClick={this.stopPropagation}>
                <ActionMenu
                    item={this.props.item}
                    plan={planningItem}
                    user={this.props.user}
                    group={this.props.group}
                    actions={this.props.actions}
                    onActionList={this.props.onActionList}
                    showActions={this.props.showActions}
                    showShortcutActions={!this.props.showShortcutActionIcons}
                />

                {!this.props.showShortcutActionIcons ? null : this.props.actions.map((action: any) => action.shortcut && (
                    <ActionButton
                        key={action.name}
                        className="icon-button icon-button--primary"
                        action={action}
                        isVisited={action.visited && action.visited(this.props.user, this.props.item)}
                        item={this.props.item}
                    />
                ))}
            </div>
        ));
    }

    renderMobile() {
        const {item, planningId} = this.props;
        const planningItem = (get(item, 'planning_items') || []).find((p: any) => p.guid === planningId) || {};
        const internalNote = getInternalNote(item, planningItem);

        return this.renderListItem(true, (
            <div className='wire-articles__item-actions ms-0' onClick={this.stopPropagation}>
                <AgendaInternalNote
                    internalNote={internalNote}
                    onlyIcon={true}
                    alignCenter={true}
                    noMargin={true}
                    marginRightAuto={true}
                    borderRight={true}
                    noPaddingRight={true}
                />

                {!this.props.showShortcutActionIcons ? null : this.props.actions.map((action: any) => action.shortcut && (
                    <ActionButton
                        key={action.name}
                        className="icon-button icon-button--primary"
                        action={action}
                        isVisited={action.visited && action.visited(this.props.user, this.props.item)}
                        item={this.props.item} />
                ))}

                {this.props.actions.length && (
                    <ActionMenu
                        item={this.props.item}
                        plan={planningItem}
                        user={this.props.user}
                        group={this.props.group}
                        actions={this.props.actions}
                        onActionList={this.props.onActionList}
                        showActions={this.props.showActions}
                        showShortcutActions={!this.props.showShortcutActionIcons}
                    />
                )}
            </div>
        ));
    }

    render() {
        return isMobilePhone() ?
            this.renderMobile() :
            this.renderNonMobile();
    }
}

AgendaListItem.propTypes = {
    item: PropTypes.object.isRequired,
    group: PropTypes.string,
    isActive: PropTypes.bool.isRequired,
    isSelected: PropTypes.bool.isRequired,
    isRead: PropTypes.bool.isRequired,
    onClick: PropTypes.func.isRequired,
    onDoubleClick: PropTypes.func.isRequired,
    onActionList: PropTypes.func.isRequired,
    showActions: PropTypes.bool.isRequired,
    toggleSelected: PropTypes.func.isRequired,
    actions: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string,
        action: PropTypes.func,
    })),
    isExtended: PropTypes.bool.isRequired,
    user: PropTypes.string,
    actioningItem: PropTypes.object,
    resetActioningItem: PropTypes.func,
    planningId: PropTypes.string,
    showShortcutActionIcons: PropTypes.bool,
    listConfig: PropTypes.object,
};

export default AgendaListItem;
