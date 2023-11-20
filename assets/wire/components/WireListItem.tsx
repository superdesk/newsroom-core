import React from 'react';
import classNames from 'classnames';

import {IArticle, IItemAction, IUser, IListConfig, IAgendaItem} from 'interfaces';
import {
    gettext,
    wordCount,
    characterCount,
    LIST_ANIMATIONS,
    getSlugline,
} from 'utils';
import {
    getImageForList,
    showItemVersions,
    shortText,
    isKilled,
    getCaption,
    shortHighlightedtext,
    getVersionsLabelText,
} from 'wire/utils';

import ActionButton from 'components/ActionButton';

import ListItemPreviousVersions from './ListItemPreviousVersions';
import WireListItemIcons from './WireListItemIcons';
import ActionMenu from '../../components/ActionMenu';
import WireListItemDeleted from './WireListItemDeleted';
import {Embargo} from './fields/Embargo';
import {UrgencyItemBorder, UrgencyLabel} from './fields/UrgencyLabel';
import {FieldComponents} from './fields';

const DEFAULT_META_FIELDS = ['source', 'charcount', 'versioncreated'];
const DEFAULT_COMPACT_META_FIELDS = ['versioncreated'];

function getShowVersionText(
    item: IArticle,
    isExpanded: boolean,
    itemCount: number,
    matchCount: number,
    isExtended: boolean
): string {
    const versionLabelText = getVersionsLabelText(item, itemCount > 1);

    if (isExpanded) {
        return (isExtended && matchCount) ?
            gettext(
                'Hide previous {{ versionsLabel }} ({{ count }}) - {{ matches }} matches',
                {
                    versionsLabel: versionLabelText,
                    matches: matchCount,
                    count: itemCount,
                }
            ) :
            gettext(
                'Hide previous {{ versionsLabel }} ({{ count }})',
                {
                    versionsLabel: versionLabelText,
                    count: itemCount,
                }
            );
    } else {
        return (isExtended && matchCount) ?
            gettext(
                'Show previous {{ versionsLabel }} ({{ count }}) - {{ matches }} matches',
                {
                    versionsLabel: versionLabelText,
                    matches: matchCount,
                    count: itemCount,
                }
            ) :
            gettext(
                'Show previous {{ versionsLabel }} ({{ count }})',
                {
                    versionsLabel: versionLabelText,
                    count: itemCount,
                }
            );
    }
}

interface IProps {
    item: IArticle;
    isActive: boolean;
    isSelected: boolean;
    isRead: boolean;
    showActions: boolean;
    isExtended: boolean;
    matchedIds: Array<IArticle['_id']>;
    isSearchFiltered: boolean;
    showShortcutActionIcons: boolean;
    user: IUser['_id'];
    context: string;
    contextName: string;
    listConfig: IListConfig;
    filterGroupLabels: {[field: string]: string};
    actions: Array<IItemAction>;
    onClick(item: IArticle): void;
    onDoubleClick(item: IArticle): void;
    onActionList(event: React.MouseEvent, item: IArticle, group?: string, plan?: IAgendaItem): void;
    toggleSelected(): void;
}

interface IState {
    previousVersions: boolean;
}

class WireListItem extends React.Component<IProps, IState> {
    static defaultProps = {matchedIds: []};
    wordCount: number;
    characterCount: number;
    dom: {article: HTMLElement | null};

    constructor(props: IProps) {
        super(props);
        this.wordCount = wordCount(props.item);
        this.characterCount = characterCount(props.item);
        this.state = {previousVersions: false};
        this.onKeyDown = this.onKeyDown.bind(this);
        this.togglePreviousVersions = this.togglePreviousVersions.bind(this);

        this.dom = {article: null};
    }

    onKeyDown(event: React.KeyboardEvent) {
        switch (event.key) {
        case ' ': // on space toggle selected item
            this.props.toggleSelected();
            break;

        default:
            return;
        }

        event.preventDefault();
    }

    togglePreviousVersions(event: React.MouseEvent) {
        event.stopPropagation();
        this.setState({previousVersions: !this.state.previousVersions});
    }

    componentDidMount() {
        if (this.props.isActive && this.dom.article) {
            this.dom.article.focus();
        }
    }

    stopPropagation(event: React.MouseEvent) {
        event.stopPropagation();
    }

    render() {
        const {
            item,
            onClick,
            onDoubleClick,
            isExtended,
            listConfig,
        } = this.props;

        if (this.props.item.deleted === true) {
            return (
                <WireListItemDeleted
                    item={this.props.item}
                    contextName={this.props.contextName}
                />
            );
        }

        const cardClassName = classNames(
            'wire-articles__item-wrap col-12 wire-item'
        );
        const wrapClassName = classNames(
            'wire-articles__item wire-articles__item--wire wire-articles__item--list',
            {
                'wire-articles__item--visited': this.props.isRead,
                'wire-articles__item--open': this.props.isActive,
                'wire-articles__item--selected': this.props.isSelected,
            }
        );
        const selectClassName = classNames('no-bindable-select', {
            'wire-articles__item-select--visible': !LIST_ANIMATIONS,
            'wire-articles__item-select': LIST_ANIMATIONS,
        });
        const listImage = getImageForList(item);
        const isMarketPlace = this.props.context === 'aapX';
        const fields = listConfig.metadata_fields || DEFAULT_META_FIELDS;
        const compactFields = listConfig.compact_metadata_fields || DEFAULT_COMPACT_META_FIELDS;
        const matchedIds = this.props.isSearchFiltered ? this.props.matchedIds : [];
        const matchedAncestors = matchedIds.filter((id: any) => (item.ancestors || []).includes(id));

        return (
            <article
                key={item._id}
                className={cardClassName}
                ref={(elem: any) => this.dom.article = elem}
                onClick={() => onClick(item)}
                onDoubleClick={() => onDoubleClick(item)}
                onKeyDown={this.onKeyDown}
            >
                <UrgencyItemBorder item={item} listConfig={listConfig} />
                <div className={wrapClassName} tabIndex={0}>
                    <div className="wire-articles__item-text-block">
                        <h4 className="wire-articles__item-headline">
                            <div
                                className={selectClassName}
                                onClick={this.stopPropagation}
                            >
                                <label className="circle-checkbox">
                                    <input
                                        type="checkbox"
                                        className="css-checkbox"
                                        checked={this.props.isSelected}
                                        onChange={this.props.toggleSelected}
                                    />
                                    <i></i>
                                </label>
                            </div>
                            <div className="wire-articles__item-headline-inner">
                                {!isExtended && (
                                    <WireListItemIcons
                                        item={item}
                                        divider={false}
                                    />
                                )}
                                <Embargo item={item} />
                                <UrgencyLabel item={item} listConfig={listConfig} filterGroupLabels={this.props.filterGroupLabels} />
                                {item.es_highlight && item.es_highlight.headline ? <div
                                    dangerouslySetInnerHTML={({__html: item.es_highlight.headline && item.es_highlight.headline[0]})}
                                /> : item.headline}
                            </div>
                        </h4>

                        {isExtended && !isMarketPlace && (
                            <div className="wire-articles__item__meta">
                                <WireListItemIcons item={item} />
                                <div className="wire-articles__item__meta-info">
                                    <span className="meta-info-slugline bold">
                                        {item.es_highlight && item.es_highlight.slugline ? <div
                                            dangerouslySetInnerHTML={({__html:item.es_highlight.slugline && item.es_highlight.slugline[0]})}
                                        /> : getSlugline(item, true)}
                                    </span>
                                    <span className="meta-info-row">
                                        <FieldComponents
                                            config={fields}
                                            item={item}
                                            fieldProps={{
                                                listConfig,
                                                isItemDetail: false,
                                            }}
                                        />
                                    </span>
                                </div>
                            </div>
                        )}

                        {isExtended &&
                            isMarketPlace && [
                            <div
                                key="mage"
                                className="wire-articles__item__meta"
                            >
                                <img
                                    src={`/theme/logo/${item.source}.png`}
                                    alt={item.source}
                                />
                            </div>,
                            <div
                                key="meta"
                                className="wire-articles__item__meta"
                            >
                                <WireListItemIcons item={item} />
                                <div className="wire-articles__item__meta-info">
                                    <span>
                                        {this.wordCount} {gettext('words')}
                                    </span>
                                </div>
                            </div>,
                        ]}
                        {!isExtended && (
                            <div className="wire-articles__item__meta">
                                <div className="wire-articles__item__meta-info">
                                    <span>
                                        <FieldComponents
                                            config={compactFields}
                                            item={item}
                                            fieldProps={{
                                                listConfig,
                                                isItemDetail: false,
                                            }}
                                        />
                                    </span>
                                </div>
                            </div>
                        )}

                        {isExtended && (
                            <div className="wire-articles__item__text">
                                {item.es_highlight && item.es_highlight.body_html ? <div
                                    dangerouslySetInnerHTML={({__html: shortHighlightedtext(item.es_highlight.body_html[0], 40)})}
                                /> : <p>{shortText(item, 40, listConfig)}</p>}
                            </div>
                        )}

                        {showItemVersions(item) && (
                            <div
                                className="no-bindable wire-articles__item__versions-btn"
                            >
                                <button
                                    className={classNames(
                                        'label label-rounded label--green mt-1 mt-md-2',
                                        {
                                            'bg-transparent': !matchedIds.length,
                                            'text-primary': !matchedIds.length,
                                        }
                                    )}
                                    onClick={this.togglePreviousVersions}
                                >
                                    {getShowVersionText(
                                        this.props.item,
                                        this.state.previousVersions,
                                        item.ancestors?.length ?? 0,
                                        matchedAncestors.length,
                                        isExtended
                                    )}
                                </button>
                            </div>
                        )}
                    </div>

                    {isExtended && !isKilled(item) && listImage != null && (
                        <div className="wire-articles__item-image">
                            <figure>
                                <img
                                    src={listImage.href}
                                    alt={getCaption(listImage.item)}
                                />
                            </figure>
                        </div>
                    )}

                    <div
                        className="wire-articles__item-actions"
                        onClick={this.stopPropagation}
                    >
                        <ActionMenu
                            item={this.props.item}
                            user={this.props.user}
                            actions={this.props.actions}
                            onActionList={this.props.onActionList}
                            showActions={this.props.showActions}
                            showShortcutActions={!this.props.showShortcutActionIcons}
                        />

                        {!this.props.showShortcutActionIcons ? null : this.props.actions.map(
                            (action: any) => (
                                action.shortcut && (
                                    <ActionButton
                                        key={action.name}
                                        className="icon-button icon-button--primary"
                                        action={action}
                                        isVisited={
                                            action.visited &&
                                            action.visited(
                                                this.props.user,
                                                this.props.item
                                            )
                                        }
                                        item={this.props.item}
                                    />
                                )
                            )
                        )}
                    </div>
                </div>

                {this.state.previousVersions && (
                    <ListItemPreviousVersions
                        item={this.props.item}
                        isPreview={false}
                        displayConfig={this.props.listConfig}
                        matchedIds={matchedIds}
                    />
                )}
            </article>
        );
    }
}

export default WireListItem;
