import React from 'react';
import {connect} from 'react-redux';
import classNames from 'classnames';

import {IArticle, IListConfig} from 'interfaces';
import {ICardProps} from '../utils';
import {characterCount, getSlugline, wordCount} from 'utils';
import {isKilled, getCaption, getImageForList, shortHighlightedtext, shortText} from 'wire/utils';

import {filterGroupsToLabelMap} from 'search/selectors';

import {DEFAULT_META_FIELDS} from 'wire/components/WireListItem';
import WireListItemIcons from 'wire/components/WireListItemIcons';
import {FieldComponents} from 'wire/components/fields';
import {Embargo} from 'wire/components/fields/Embargo';
import {UrgencyItemBorder, UrgencyLabel} from 'wire/components/fields/UrgencyLabel';
import CardRow from './CardRow';

interface IWireListCardItemProps {
    item: IArticle;
    openItem: (item: IArticle, cardId: string) => void;
    cardId: string;
    listConfig: IListConfig;
    filterGroupLabels: {[field: string]: string};
}

class WireListPanel extends React.Component<IWireListCardItemProps> {
    wordCount: number;
    characterCount: number;

    constructor(props: IWireListCardItemProps) {
        super(props);

        this.wordCount = wordCount(props.item);
        this.characterCount = characterCount(props.item);
    }

    render(): React.ReactNode {
        const cardClassName = classNames('wire-articles__item-wrap col-12 wire-item');
        const wrapClassName = classNames('wire-articles__item wire-articles__item--wire wire-articles__item--list');
        const listImage = getImageForList(this.props.item);
        const {item, listConfig, cardId, openItem} = this.props;

        const onItemClick = () => {
            openItem(item, cardId);
        };

        return (
            <article
                key={item._id}
                className={cardClassName}
                onClick={onItemClick}
                data-test-id={`wire-${item._id}`}
                data-test-value={item._id}
            >
                <UrgencyItemBorder item={item} listConfig={listConfig} />
                <div className={wrapClassName} tabIndex={0}>
                    <div className="wire-articles__item-text-block">
                        <h4 className="wire-articles__item-headline">
                            <div className="wire-articles__item-headline-inner">
                                <Embargo item={item} />
                                <UrgencyLabel item={item} listConfig={listConfig} filterGroupLabels={this.props.filterGroupLabels} />
                                {item.es_highlight && item.es_highlight.headline ? <div
                                    dangerouslySetInnerHTML={({__html: item.es_highlight.headline && item.es_highlight.headline[0]})}
                                /> : item.headline}
                            </div>
                        </h4>
                        <div className="wire-articles__item__meta">
                            <WireListItemIcons item={item} />
                            <div className="wire-articles__item__meta-info">
                                <span className="meta-info-slugline bold">
                                    {item.es_highlight && item.es_highlight.slugline ? <div
                                        dangerouslySetInnerHTML={({__html: item.es_highlight.slugline && item.es_highlight.slugline[0]})}
                                    /> : getSlugline(item, true)}
                                </span>
                                <span className="meta-info-row">
                                    <FieldComponents
                                        config={this.props.listConfig.metadata_fields || DEFAULT_META_FIELDS}
                                        item={item}
                                        fieldProps={{
                                            listConfig: listConfig,
                                            isItemDetail: false,
                                        }}
                                    />
                                </span>
                            </div>
                        </div>

                        <div className="wire-articles__item__text">
                            {item.es_highlight && item.es_highlight.body_html ? <div
                                dangerouslySetInnerHTML={({__html: shortHighlightedtext(item.es_highlight.body_html[0], 40)})}
                            /> : <p>{shortText(item, 40, listConfig)}</p>}
                        </div>

                    </div>

                    {!isKilled(item) && listImage != null && (
                        <div className="wire-articles__item-image">
                            <figure>
                                <img
                                    src={listImage.href}
                                    alt={getCaption(listImage.item)}
                                />
                            </figure>
                        </div>
                    )}
                </div>
            </article>
        );
    }
}

interface IWireListCardProps extends ICardProps {
    filterGroupLabels: {[field: string]: string};
}

const WireListCardComponent: React.ComponentType<IWireListCardProps> = (props: IWireListCardProps) => {
    return (
        <CardRow title={props.title} id={props.id} isActive={props.isActive} onMoreNewsClicked={props.onMoreNewsClicked}>
            {props.items.map((item: IArticle) => (
                <WireListPanel
                    key={item._id}
                    item={item}
                    cardId={props.cardId}
                    openItem={props.openItem}
                    listConfig={props.listConfig}
                    filterGroupLabels={props.filterGroupLabels}
                />
            ))}
        </CardRow>
    );
};

const mapStateToProps = (state: any) => ({filterGroupLabels: filterGroupsToLabelMap(state)});
const WireListCard = connect(mapStateToProps)(WireListCardComponent);


export default WireListCard;
