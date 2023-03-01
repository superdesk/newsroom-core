import React from 'react';
import PropTypes from 'prop-types';
import {isEmpty} from 'lodash';
import PreviewMeta from './PreviewMeta';
import PreviewTags from './PreviewTags';
import AgendaLinks from './AgendaLinks';
import {isDisplayed, gettext, formatDate, formatTime} from 'utils';
import ListItemPreviousVersions from './ListItemPreviousVersions';
import ListItemNextVersion from './ListItemNextVersion';
import {
    getItemMedia,
    showItemVersions,
    isKilled,
    DISPLAY_ABSTRACT,
    isPreformatted,
    isCustomRendition,
    getPictureList,
} from 'wire/utils';
import types from 'wire/types';
import Content from 'ui/components/Content';
import ContentHeader from 'ui/components/ContentHeader';
import ContentBar from 'ui/components/ContentBar';
import ArticleItemDetails from 'ui/components/ArticleItemDetails';
import ArticleContent from 'ui/components/ArticleContent';
import ArticlePicture from 'ui/components/ArticlePicture';
import ArticleMedia from  'ui/components/ArticleMedia';
import ArticleContentWrapper from 'ui/components/ArticleContentWrapper';
import ArticleContentInfoWrapper from 'ui/components/ArticleContentInfoWrapper';
import ArticleHeadline from 'ui/components/ArticleHeadline';
import ArticleAbstract from 'ui/components/ArticleAbstract';
import ArticleBodyHtml from 'ui/components/ArticleBodyHtml';
import ArticleBody from 'ui/components/ArticleBody';
import ArticleAuthor from 'ui/components/ArticleAuthor';
import ArticleEmbargoed from 'ui/components/ArticleEmbargoed';
import PreviewEdnote from './PreviewEdnote';
import WireActionButtons from './WireActionButtons';
import {Authors} from './fields/Authors';

function ItemDetails({
    item,
    user,
    actions,
    topics,
    onClose,
    detailsConfig,
    downloadMedia,
    followStory,
    listConfig,
    filterGroupLabels,
}) {
    const pictures = getPictureList(item);
    const media = getItemMedia(item);
    const itemType = isPreformatted(item) ? 'preformatted' : 'text';

    return (
        <Content type="item-detail">
            <ContentHeader>
                <ContentBar onClose={onClose}>
                    <WireActionButtons
                        item={item}
                        user={user}
                        topics={topics}
                        actions={actions}
                        followStory={followStory}
                    />
                </ContentBar>
            </ContentHeader>
            <ArticleItemDetails>
                <ArticleContent>
                    {pictures && pictures.map((pic) => (
                        <ArticlePicture
                            key={pic._id}
                            picture={pic}
                            isKilled={isKilled(item)}
                            isCustomRendition={isCustomRendition(pic)}
                        />
                    ))}
                    <ArticleContentWrapper itemType={itemType}>
                        <ArticleBody itemType={itemType}>
                            <ArticleEmbargoed item={item} />
                            <div className='wire-column__preview__date pb-2'>
                                {gettext('Published on {{ date }} at {{ time }}', {
                                    date: formatDate(item.versioncreated),
                                    time: formatTime(item.versioncreated),
                                })}
                            </div>
                            {isDisplayed('headline', detailsConfig) && <ArticleHeadline item={item}/>}
                            <ArticleAuthor item={item} displayConfig={detailsConfig} />
                            {isDisplayed('abstract', detailsConfig) &&
                            <ArticleAbstract item={item} displayAbstract={DISPLAY_ABSTRACT}/>}
                            {isDisplayed('body_html', detailsConfig) && <ArticleBodyHtml item={item}/>}
                            {!isEmpty(media) && media.map((media) => <ArticleMedia
                                key={media.guid}
                                media={media}
                                isKilled={isKilled(item)}
                                download={downloadMedia}
                            />)}
                        </ArticleBody>

                        {isDisplayed('metadata_section', detailsConfig) && (
                            <PreviewMeta item={item} isItemDetail={true} displayConfig={detailsConfig}
                                listConfig={listConfig}
                                filterGroupLabels={filterGroupLabels}
                            />
                        )}
                        <ArticleContentInfoWrapper>
                            {isDisplayed('tags_section', detailsConfig) &&
                                <PreviewTags item={item} isItemDetail={true} displayConfig={detailsConfig}/>}

                            {isDisplayed('authors', detailsConfig) && (
                                <Authors item={item} />
                            )}

                            {isDisplayed('ednotes_section', detailsConfig) &&
                                <PreviewEdnote item={item} />}

                            {isDisplayed('item_versions', detailsConfig) && showItemVersions(item, true) &&
                                <ListItemNextVersion item={item} displayConfig={detailsConfig}  />
                            }
                            {isDisplayed('item_versions', detailsConfig) && showItemVersions(item) &&
                                <ListItemPreviousVersions item={item} displayConfig={detailsConfig} isPreview={true}/>
                            }

                            {isDisplayed('agenda_links', detailsConfig) && <AgendaLinks item={item} />}
                        </ArticleContentInfoWrapper>
                    </ArticleContentWrapper>
                </ArticleContent>
            </ArticleItemDetails>
        </Content>
    );
}

ItemDetails.propTypes = {
    item: types.item.isRequired,
    user: types.user.isRequired,
    topics: types.topics.isRequired,
    actions: types.actions,
    listConfig: PropTypes.object,
    detailsConfig: PropTypes.object,
    filterGroupLabels: PropTypes.object,

    onClose: PropTypes.func,
    downloadMedia: PropTypes.func,
    followStory: PropTypes.func,
};

export default ItemDetails;

