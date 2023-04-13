import React from 'react';
import PropTypes from 'prop-types';
import {isEmpty} from 'lodash';
import PreviewMeta from './PreviewMeta';
import PreviewTags from './PreviewTags';
import AgendaLinks from './AgendaLinks';
import ListItemPreviousVersions from './ListItemPreviousVersions';
import ListItemNextVersion from './ListItemNextVersion';
import PreviewEdnote from './PreviewEdnote';
import WireActionButtons from './WireActionButtons';
import {Authors} from './fields/Authors';
import {
    getItemMedia,
    showItemVersions,
    isEqualItem,
    isKilled,
    DISPLAY_ABSTRACT,
    isCustomRendition,
    getPictureList,
} from 'assets/wire/utils';
import ArticleAbstract from 'assets/ui/components/ArticleAbstract';
import ArticleAuthor from 'assets/ui/components/ArticleAuthor';
import ArticleBody from 'assets/ui/components/ArticleBody';
import ArticleBodyHtml from 'assets/ui/components/ArticleBodyHtml';
import ArticleContent from 'assets/ui/components/ArticleContent';
import ArticleContentInfoWrapper from 'assets/ui/components/ArticleContentInfoWrapper';
import ArticleContentWrapper from 'assets/ui/components/ArticleContentWrapper';
import ArticleEmbargoed from 'assets/ui/components/ArticleEmbargoed';
import ArticleHeadline from 'assets/ui/components/ArticleHeadline';
import ArticleItemDetails from 'assets/ui/components/ArticleItemDetails';
import ArticleMedia from 'assets/ui/components/ArticleMedia';
import ArticlePicture from 'assets/ui/components/ArticlePicture';
import Content from 'assets/ui/components/Content';
import ContentBar from 'assets/ui/components/ContentBar';
import ContentHeader from 'assets/ui/components/ContentHeader';
import {gettext, formatDate, formatTime, isDisplayed} from 'assets/utils';
import types from 'fetch-mock';

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
}: any) {
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
            <ArticleItemDetails disableTextSelection={detailsConfig.disable_text_selection}>
                <ArticleContent>
                    {pictures && pictures.map((pic: any) => (
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
                            {!isEmpty(media) && media.map((media: any) => <ArticleMedia
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

