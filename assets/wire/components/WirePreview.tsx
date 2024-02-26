import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {isEmpty} from 'lodash';

import {isDisplayed} from 'utils';
import {
    getFeatureMedia,
    getOtherMedia,
    showItemVersions,
    isEqualItem,
    isKilled,
    DISPLAY_ABSTRACT,
    isCustomRendition,
    getPictureList
} from 'wire/utils';
import types from 'wire/types';

import Preview from 'ui/components/Preview';
import ArticleSlugline from 'ui/components/ArticleSlugline';
import ArticleAuthor from  'ui/components/ArticleAuthor';
import ArticlePicture from  'ui/components/ArticlePicture';
import ArticleMedia from  'ui/components/ArticleMedia';
import ArticleHeadline from 'ui/components/ArticleHeadline';
import ArticleAbstract from 'ui/components/ArticleAbstract';
import ArticleBodyHtml from 'ui/components/ArticleBodyHtml';
import ArticleEmbargoed from 'ui/components/ArticleEmbargoed';


import ListItemPreviousVersions from './ListItemPreviousVersions';
import PreviewTags from './PreviewTags';
import PreviewMeta from './PreviewMeta';
import AgendaLinks from './AgendaLinks';
import PreviewEdnote from './PreviewEdnote';
import WireActionButtons from './WireActionButtons';
import {Authors} from './fields/Authors';
import {downloadMedia} from '../actions';


class WirePreview extends React.PureComponent<any, any> {
    static propTypes: any;
    preview: any;
    constructor(props: any) {
        super(props);
    }

    componentDidUpdate(nextProps: any) {
        if (!isEqualItem(nextProps.item, this.props.item)) {
            this.preview.scrollTop = 0; // reset scroll on change
        }
    }

    render() {
        const {item, user, actions, followStory, topics, previewConfig, downloadMedia, listConfig, filterGroupLabels} = this.props;
        const featureMedia = getFeatureMedia(item);
        const media = getOtherMedia(item);
        const allMedia = getPictureList(item)
        const previousVersions = 'preview_versions';
        return (
            <Preview onCloseClick={this.props.closePreview} published={item.versioncreated}>
                <div className='wire-column__preview__top-bar'>
                    <WireActionButtons
                        user={user}
                        item={item}
                        topics={topics}
                        actions={actions}
                        followStory={followStory}
                        previewConfig={previewConfig}
                    />
                </div>
                <div
                    id='preview-article'
                    ref={(preview: any) => this.preview = preview}
                    className={classNames(
                        'wire-column__preview__content',
                        {noselect: this.props.previewConfig.disable_text_selection}
                    )}
                >
                    <ArticleEmbargoed item={item} />
                    {isDisplayed('slugline', previewConfig) && <ArticleSlugline item={item}/>}
                    {isDisplayed('headline', previewConfig) && <ArticleHeadline item={item}/>}
                    {(isDisplayed('byline', previewConfig) || isDisplayed('located', previewConfig)) &&
                        <ArticleAuthor item={item} displayConfig={previewConfig} />}
                    {featureMedia == null ? null : (
                        featureMedia.type === 'picture' ? (
                            <ArticlePicture
                                picture={featureMedia}
                                isKilled={isKilled(item)}
                                isCustomRendition={isCustomRendition(featureMedia)}
                            />
                        ) : (
                            <ArticleMedia
                                media={featureMedia}
                                isKilled={isKilled(item)}
                                download={downloadMedia}
                            />
                        )
                    )}
                    {allMedia == null ? null : allMedia
                    .filter((mediaItem) => mediaItem.guid !== featureMedia?.guid) // Filter out feature media
                    .map((data) => {
                        return (
                            data.type === 'picture' ? (
                            <ArticlePicture
                                key={data?.guid}
                                picture={data}
                                isKilled={isKilled(item)}
                                isCustomRendition={isCustomRendition(data)}
                            />
                        ) : (
                            <ArticleMedia
                                key={data.guid}
                                media={data}
                                isKilled={isKilled(item)}
                                download={downloadMedia}
                            />
                        )
                    )
                    })}
                    {isDisplayed('metadata_section', previewConfig) &&
                    <PreviewMeta item={item} isItemDetail={false} inputRef={previousVersions} displayConfig={previewConfig} listConfig={listConfig}
                        filterGroupLabels={filterGroupLabels} />}
                    {isDisplayed('abstract', previewConfig) &&
                    <ArticleAbstract item={item} displayAbstract={DISPLAY_ABSTRACT}/>}
                    {isDisplayed('body_html', previewConfig) && <ArticleBodyHtml item={item}/>}

                    {media == null ? null : media.map((mediaItem) => (
                        <ArticleMedia
                            key={mediaItem.guid}
                            media={mediaItem}
                            isKilled={isKilled(item)}
                            download={downloadMedia}
                        />
                    ))}

                    {isDisplayed('tags_section', previewConfig) &&
                        <PreviewTags item={item} isItemDetail={false} displayConfig={previewConfig}/>}

                    {isDisplayed('authors', previewConfig) && (
                        <Authors item={item} />
                    )}

                    {isDisplayed('ednotes_section', previewConfig) &&
                                <PreviewEdnote item={item} />}

                    {isDisplayed('item_versions', previewConfig) && showItemVersions(item) &&
                        <ListItemPreviousVersions
                            item={item}
                            isPreview={true}
                            inputId={previousVersions}
                            displayConfig={previewConfig}
                        />
                    }
                    {isDisplayed('agenda_links', previewConfig) &&
                        <AgendaLinks item={item} preview={true} />}
                </div>
            </Preview>
        );
    }
}

WirePreview.propTypes = {
    user: types.user,
    item: types.item.isRequired,
    topics: types.topics,
    actions: types.actions,
    previewConfig: types.previewConfig,

    followStory: PropTypes.func,
    closePreview: PropTypes.func,
    downloadMedia: PropTypes.func,
    listConfig: PropTypes.object,
    filterGroupLabels: PropTypes.object,
};

export default WirePreview;
