import React from 'react';
import classNames from 'classnames';

import {IAgendaItem, IAgendaListGroup, IItemAction, IListConfig, IUser} from 'interfaces';

import ActionButton from 'components/ActionButton';
import AgendaListItemIcons from './AgendaListItemIcons';
import AgendaItemTimeUpdater from './AgendaItemTimeUpdater';
import AgendaInternalNote from './AgendaInternalNote';

import {
    hasCoverages,
    isCanceled,
    isPostponed,
    isRescheduled,
    getName,
    isWatched,
    getHighlightedDescription,
    getHighlightedName,
    getInternalNote,
} from '../utils';
import ActionMenu from '../../components/ActionMenu';
import {LIST_ANIMATIONS, isMobilePhone, gettext} from 'utils';
import TopStoryLabel from './TopStoryLabel';
import ToBeConfirmedLabel from './ToBeConfirmedLabel';
import {LabelGroup} from 'ui/components/LabelGroup';

interface IProps {
    item: IAgendaItem;
    group: IAgendaListGroup;
    isActive: boolean;
    isSelected: boolean;
    isRead: boolean;
    showActions: boolean;
    actions: Array<IItemAction>;
    isExtended: boolean;
    user: IUser['_id'];
    actioningItem?: IAgendaItem;
    planningId?: IAgendaItem['_id'];
    showShortcutActionIcons: boolean;
    listConfig: IListConfig;

    onClick(item: IAgendaItem, date: string, planningId?: IAgendaItem['_id']): void;
    onDoubleClick(item: IAgendaItem, date: string, planningId?: IAgendaItem['_id']): void;
    onActionList(event: React.MouseEvent, item: IAgendaItem, date: string, plan?: IAgendaItem): void;
    toggleSelected(): void;
    resetActioningItem(): void;
}

const isHTML = (value: string) => {
    const doc = new DOMParser().parseFromString(value, 'text/html');
    return Array.from(doc.body.childNodes).some(node => node.nodeType === 1);
};

class AgendaListItem extends React.Component<IProps> {
    dom: {article: HTMLElement | null};

    constructor(props: IProps) {
        super(props);
        this.dom = {article: null};
        this.onKeyDown = this.onKeyDown.bind(this);
        this.setArticleRef = this.setArticleRef.bind(this);
        this.onArticleClick = this.onArticleClick.bind(this);
        this.onArticleDoubleClick = this.onArticleDoubleClick.bind(this);
        this.onMouseEnter = this.onMouseEnter.bind(this);
    }

    onKeyDown(event: React.KeyboardEvent) {
        switch (event.key) {
        case ' ':  // on space toggle selected item
            this.props.toggleSelected();
            break;

        default:
            return;
        }

        event.preventDefault();
    }

    setArticleRef(elem: HTMLElement) {
        this.dom.article = elem;
    }

    onArticleClick() {
        this.props.onClick(this.props.item, this.props.group.date, this.props.planningId);
    }

    onArticleDoubleClick() {
        this.props.onDoubleClick(this.props.item, this.props.group.date, this.props.planningId);
    }

    onMouseEnter() {
        if (this.props.actioningItem && this.props.actioningItem._id !== this.props.item._id) {
            this.props.resetActioningItem();
        }
    }

    shouldComponentUpdate(nextProps: Readonly<IProps>) {
        const {props} = this;
        const currentBookmarked = (props.item.bookmarks || []).includes(props.user);
        const nextBookmarked = (nextProps.item.bookmarks || []).includes(nextProps.user);

        return props.item._etag !== nextProps.item._etag ||
            props.isActive !== nextProps.isActive ||
            props.isSelected !== nextProps.isSelected ||
            props.isExtended !== nextProps.isExtended ||
            props.actioningItem?._id === props.item._id ||
            nextProps.actioningItem?._id === props.item._id ||
            props.isRead !== nextProps.isRead ||
            currentBookmarked !== nextBookmarked ||
            nextBookmarked ||
            isWatched(props.item, props.user) !== isWatched(nextProps.item, nextProps.user);
    }

    componentDidMount() {
        if (this.props.isActive === true && this.dom.article != null) {
            this.dom.article.focus();
        }
    }

    stopPropagation(event: React.MouseEvent) {
        event.stopPropagation();
    }

    getClassNames(isExtended: boolean) {
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

    getSegments(description: string) {
        const dom = new DOMParser().parseFromString(description.replace(/\n/g, '<br />'), 'text/html');
        const arrayOfParagraphs = dom.body.querySelectorAll('p');

        const getSegmentCount = (p: HTMLParagraphElement): number => {
            // adding one because if there are 2 <br> tags it means there are 3 segments
            return p.getElementsByTagName('br').length + 1;
        };

        const descriptionHTMLArr: HTMLParagraphElement[] = [];
        let segmentsRemainingToBeAdded = 3;
        let paragraphsInnerText = '';

        arrayOfParagraphs.forEach(paragraph => {
            if (segmentsRemainingToBeAdded > 0) {
                paragraphsInnerText += paragraph.innerText;
                paragraph.innerHTML = paragraph.innerHTML.split('<br>').filter((p: string) => p.trim() !== '').slice(0, segmentsRemainingToBeAdded).join('<br>');

                segmentsRemainingToBeAdded = segmentsRemainingToBeAdded - getSegmentCount(paragraph);

                descriptionHTMLArr.push(paragraph);
            }
        });

        return {
            /**
             * keep in mind that first 3 segments might be 1-3 paragraphs
             */
            firstThreeSegments: descriptionHTMLArr,
            hasMoreContent: dom.body.innerText.length > paragraphsInnerText.length,
        };
    }

    getSearchSegments(_description: string) {
        const domWithoutHighlightedText = new DOMParser().parseFromString(_description, 'text/html');
        domWithoutHighlightedText.querySelectorAll('span.es-highlight').forEach((element) => {
            element.remove();
        });

        const description = isHTML(domWithoutHighlightedText.body.outerHTML) ? _description : _description.split('\n').map((p) => `<p>${p}</p>`).join('');

        const dom = new DOMParser().parseFromString(description.replace(/\n/g, '<br />'), 'text/html');
        const arrayOfParagraphs = dom.body.querySelectorAll('p');
        const numberOfResults = dom.body.querySelectorAll('span.es-highlight').length;

        const getSegmentCount = (p: HTMLParagraphElement): number => {
            // adding one because if there are 2 <br> tags it means there are 3 segments
            return p.getElementsByTagName('br').length + 1;
        };

        const descriptionHTMLArr: HTMLParagraphElement[] = [];
        let segmentsRemainingToBeAdded = 3;
        let paragraphsInnerText = '';

        arrayOfParagraphs.forEach((paragraph, i) => {
            const span = paragraph.getElementsByClassName('es-highlight');

            if (span.length > 0) {
                [...arrayOfParagraphs].slice(i, arrayOfParagraphs.length).forEach((paragraph, i) => {
                    if (segmentsRemainingToBeAdded > 0) {
                        paragraphsInnerText += paragraph.innerText;
                        paragraph.innerHTML = paragraph.innerHTML.split('<br>').filter((p: string) => p.trim() !== '').slice(0, segmentsRemainingToBeAdded).join('<br>');

                        segmentsRemainingToBeAdded = segmentsRemainingToBeAdded - getSegmentCount(paragraph);

                        descriptionHTMLArr.push(paragraph);
                    }
                });
            }
        });

        let numberOfRenderResults = 0;
        descriptionHTMLArr.forEach(element => {
            numberOfRenderResults += element.querySelectorAll('span.es-highlight').length;
        });

        return {
            /**
             * keep in mind that first 3 segments might be 1-3 paragraphs
             */
            firstThreeSearchSegments: descriptionHTMLArr,
            hasMoreSearchContent: dom.body.innerText.length > paragraphsInnerText.length,
            numberOfNotRenderResults: numberOfResults - numberOfRenderResults,
        };
    }

    renderListItem(isMobile: boolean, children: React.ReactNode) {
        const {item, isExtended, group, planningId, listConfig} = this.props;
        const classes = this.getClassNames(isExtended);
        const planningItem = (item.planning_items || []).find((p) => p.guid === planningId);
        const description = getHighlightedDescription(item, planningItem);
        // Show headline for adhoc planning items
        const showHeadline = item.event == null && (item.headline?.length ?? 0) > 0;
        const {firstThreeSegments, hasMoreContent} =  this.getSegments(description);
        const {firstThreeSearchSegments, hasMoreSearchContent, numberOfNotRenderResults} =  this.getSearchSegments(description);

        const renderDescription = (() => {
            if (item.es_highlight != null && (item.es_highlight.definition_short ?? '').length > 0) {
                return (
                    firstThreeSearchSegments.map((paragraph, i: number) => {
                        const lastChild: boolean = firstThreeSearchSegments.length - 1 === i;
                        const showThreeDots = lastChild && hasMoreSearchContent;

                        const Wrapper: React.ComponentType<{children: React.ReactNode}> = ({children}) => {
                            if (lastChild && numberOfNotRenderResults > 0) {
                                return (
                                    <div key={i} className='d-flex gap-1 align-items-end'>
                                        {children}
                                        <span className='wire-articles__item__text--muted'>({gettext('{{n}} more', {n: numberOfNotRenderResults})})</span>
                                    </div>
                                );
                            } else {
                                return <>{children}</>;
                            }
                        };

                        return (
                            <Wrapper key={i}>
                                <div className={showThreeDots ? 'wire-articles__item__text--last-child' : ''} dangerouslySetInnerHTML={{__html: paragraph.outerHTML}} />
                            </Wrapper>
                        );
                    })
                );
            } else {
                if (isHTML(description)) {
                    return (
                        firstThreeSegments.map((paragraph, i: number) => {
                            const lastChild: boolean = firstThreeSegments.length - 1 === i;
                            const showThreeDots = lastChild && hasMoreContent;

                            return <div className={showThreeDots ? 'wire-articles__item__text--last-child' : ''} dangerouslySetInnerHTML={{__html: paragraph.outerHTML}} key={i} />;
                        })
                    );
                } else {
                    return (
                        description.split('\n').slice(0, 3).map((plainText: string, i: number, array: Array<string>) => {
                            const lastChild = array.length -1 === i;
                            const showThreeDots: boolean = lastChild && description.length > description.split('\n').slice(0, 3).join('\n').length;

                            return <p className={showThreeDots ? 'wire-articles__item__text--last-child' : ''} key={i}>{plainText}</p>;
                        })
                    );
                }
            }
        })();

        const renderTopStoryLabel = () => {
            if (group.hiddenItems.includes(item._id) === false) {
                return <TopStoryLabel item={item} config={listConfig} />;
            } else {
                return null;
            }
        };

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
                        <LabelGroup>
                            {renderTopStoryLabel()}
                            <ToBeConfirmedLabel item={item} />
                        </LabelGroup>

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
                            group={group.date}
                            planningItem={planningItem}
                            isMobilePhone={isMobile}
                            user={this.props.user}
                            listConfig={listConfig}
                        />

                        {(isMobile || isExtended) && description && (
                            <div className="wire-articles__item__text">
                                {renderDescription}
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
        const planningItem = (item.planning_items || []).find((p) => p.guid === planningId);

        return this.renderListItem(false, !this.props.actions.length ? null : (
            <div className='wire-articles__item-actions' onClick={this.stopPropagation}>
                <ActionMenu
                    item={this.props.item}
                    plan={planningItem}
                    user={this.props.user}
                    group={this.props.group.date}
                    actions={this.props.actions}
                    onActionList={this.props.onActionList}
                    showActions={this.props.showActions}
                    showShortcutActions={!this.props.showShortcutActionIcons}
                />

                {!this.props.showShortcutActionIcons ? null : this.props.actions.map((action) => action.shortcut && (
                    <ActionButton
                        key={action.name}
                        variant='primary'
                        action={action}
                        item={this.props.item}
                    />
                ))}
            </div>
        ));
    }

    renderMobile() {
        const {item, planningId} = this.props;
        const planningItem = (item.planning_items || []).find((p) => p.guid === planningId);
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

                {!this.props.showShortcutActionIcons ? null : this.props.actions.map((action) => action.shortcut && (
                    <ActionButton
                        key={action.name}
                        variant='primary'
                        action={action}
                        item={this.props.item} />
                ))}

                {this.props.actions.length && (
                    <ActionMenu
                        item={this.props.item}
                        plan={planningItem}
                        user={this.props.user}
                        group={this.props.group.date}
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

export default AgendaListItem;
