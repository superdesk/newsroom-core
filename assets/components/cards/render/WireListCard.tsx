import React from 'react';
import MoreNewsButton from './MoreNewsButton';
import classNames from 'classnames';
import {characterCount, wordCount} from 'utils';
import WireListItemIcons from 'wire/components/WireListItemIcons';
import {FieldComponents} from 'wire/components/fields';
import {Embargo} from 'wire/components/fields/Embargo';
import {UrgencyItemBorder, UrgencyLabel} from 'wire/components/fields/UrgencyLabel';
import {isKilled, getCaption, getImageForList} from 'wire/utils';
import {connect} from 'react-redux';
import {listConfigSelector} from 'ui/selectors';
import {DEFAULT_COMPACT_META_FIELDS} from 'wire/components/WireListItem';
import {IArticle, IListConfig} from 'interfaces';
import {showModal} from '@superdesk/common';
import {filterGroupsToLabelMap} from 'search/selectors';

interface IOwnProps {
    item: IArticle;
}

interface IPropsReduxStore {
    listConfig: IListConfig;
    filterGroupLabels: any;
}

type IPropsCombined = IPropsReduxStore & IOwnProps;

class WireListPanel extends React.Component<IPropsCombined> {
    wordCount: number;
    characterCount: number;

    constructor(props: IPropsCombined) {
        super(props);

        this.wordCount = wordCount(props.item);
        this.characterCount = characterCount(props.item);
    }

    render(): React.ReactNode {
        const cardClassName = classNames('wire-articles__item-wrap col-12 wire-item');
        const wrapClassName = classNames('wire-articles__item wire-articles__item--wire wire-articles__item--list');
        const listImage = getImageForList(this.props.item);
        const compactFields = this.props.listConfig.compact_metadata_fields || DEFAULT_COMPACT_META_FIELDS;
        const {item, listConfig} = this.props;
        const isExtended = false;

        // FIXME: Implement the proper subscription overlay
        const showOverlay = () => showModal(({closeModal}) => {
            return (
                <div
                    style={{
                        position: 'absolute',
                        zIndex: 2400,
                        width: '100%',
                        height: '100%',
                        background: 'white'
                    }}
                >
                    <div>subscribe</div>
                    <button type='button' onClick={closeModal}>Close modal</button>
                </div>
            );
        });
        return (
            <article
                key={item._id}
                className={cardClassName}
                onClick={() => showOverlay()}
                onDoubleClick={() => showOverlay()}
                data-test-id={`wire-${item._id}`}
                data-test-value={item._id}
            >
                <UrgencyItemBorder item={item} listConfig={listConfig} />
                <div className={wrapClassName} tabIndex={0}>
                    <div className="wire-articles__item-text-block">
                        <h4 className="wire-articles__item-headline">
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

const mapStateToProps = (state: any) => ({
    filterGroupLabels: filterGroupsToLabelMap(state),
    listConfig: listConfigSelector(state),
});

const WireListPanelConnected: React.ComponentType<IOwnProps> =
    connect<IPropsReduxStore, {}, IOwnProps>(mapStateToProps)(WireListPanel);

export interface IWireListCardProps {
    items: Array<IArticle>;
    title?: string;
}

const WireListCard: React.ComponentType<IWireListCardProps> = ({items, title}: IWireListCardProps) => {
    return (
        <div className='row'>
            <MoreNewsButton kind='product' title={title ?? ''} />
            {items.map((item: IArticle) => (<WireListPanelConnected key={item._id} item={item} />))}
        </div>
    );
};

export default WireListCard;
