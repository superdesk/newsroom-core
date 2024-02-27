import {get, isEmpty, isEqual, pickBy} from 'lodash';

import {IArticle, IContentType, IRendition} from '../interfaces';
import {getTextFromHtml, getConfig, isDisplayed} from 'utils';

export const DISPLAY_ABSTRACT = getConfig('display_abstract');


const STATUS_KILLED = 'canceled';


/**
 * Returns the item version as integer
 *
 * @param {Object} item
 * @returns {number}
 */
export function getIntVersion(item: any) {
    if (item) {
        return parseInt(item.version, 10) || 0;
    }
}

/**
 * Get videos for an item
 *
 * if item is video return it, otherwise look for featuremedia
 *
 * @param {Object} item
 * @return {Array}
 */
export function getVideos(item: any) {
    return getRelatedItemsByType(item, 'video');
}

const isMedia = (item: IArticle) => item.type === 'audio' || item.type === 'video';

/**
 *
 * @param {*} item
 */
export function getItemMedia(item: IArticle) {
    if (isMedia(item)) {
        return [item];
    }

    return Object.values(item.associations || {}).filter((assoc) => assoc != null && isMedia(assoc));
}

function getRelatedItemsByType(item: IArticle, type: string) {
    return item.type === type ? [item] : Object.values(item.associations || {}).filter((assoc) => assoc?.type === type);
}

export function getFeatureMedia(item: IArticle): IArticle | null {
    if (['picture', 'video', 'audio'].includes(item.type)) {
        return item;
    }

    const featured = item.associations?.featuremedia;

    if (featured != null && ['picture', 'video', 'audio'].includes(featured.type)) {
        return featured;
    }

    return getBodyPicture(item);
}

export function getOtherMedia(item: IArticle): Array<IArticle> | null {
    if (['picture', 'video', 'audio'].includes(item.type)) {
        return null;
    }

    return Object.entries(item.associations || {})
        .filter(([key, item]) => (
            !key.startsWith('editor_') &&
            key !== 'featuremedia' &&
            item != null &&
            ['video', 'audio'].includes(item.type)
        ))
        .map(([key, item]) => item) as IArticle[]; // null values are filtered in .filter
}

/**
 * Get picture for an item
 *
 * if item is picture return it, otherwise look for featuremedia
 *
 * @param {Object} item
 * @return {Object}
 */
export function getPicture(item: IArticle) {
    if (item.type === 'picture') {
        return item;
    }

    const featured = item.associations?.featuremedia;

    if (featured != null && featured.type === 'picture') {
        return featured;
    }

    return getBodyPicture(item);
}

function getBodyPicture(item: IArticle): IArticle | null {
    const pictures = Object.values(item.associations ?? {})
        .filter((association) => association?.type === 'picture');
    return pictures.length ? pictures[0] : null;
}

export function getPictureList(item: IArticle, {includeFeatured = false, includeEditor = false} = {}): IArticle[] {
    const pictures = Object.values(item.associations ?? {})
        .filter((association) => association?.type === 'picture') as IArticle[];

    let filteredPictures = pictures;

    if (!includeFeatured) {
        const featureMedia = getFeatureMedia(item);
        filteredPictures = featureMedia ? filteredPictures.filter((mediaItem) => mediaItem.guid !== featureMedia.guid) : filteredPictures;
    }

    if (!includeEditor) {
        const bodyMedia = getBodyPictureList(item);
        filteredPictures = filteredPictures.filter((mediaItem) => bodyMedia.includes(mediaItem));
    }

    return filteredPictures;
}

export function getBodyPictureList(item: IArticle): Array<IArticle> {
    return Object.entries(item.associations || {})
        .filter(([key, item]) => (
            !key.startsWith('editor_')))
        .map(([key, item]) => item) as IArticle[];

}

export function getGalleryMedia(item: IArticle): IArticle[] {
    return getPictureList(item, {includeFeatured: false, includeEditor: false});
}

/**
 * Get picture thumbnail rendition specs
 *
 * @param {Object} picture
 * @param {Boolean} large
 * @return {Object}
 */
export function getThumbnailRendition(picture: IArticle, large?: boolean): IRendition | undefined {
    const rendition = large ? picture.renditions?._newsroom_thumbnail_large : picture.renditions?._newsroom_thumbnail;

    return rendition ?? picture.renditions?.thumbnail;
}

export function getImageForList(item: IArticle): {item: IArticle, href: string} | undefined {
    const pictures = getPictureList(item);
    const feature = getFeatureMedia(item);
    let thumbnail: IRendition | undefined;

    if (feature) {
        thumbnail = getThumbnailRendition(feature);
        if (thumbnail != null && thumbnail.href != null) {
            return {item: feature, href: thumbnail.href};
        }
    } else {
        for (let i = 0; i < pictures.length; i++) {
            thumbnail = getThumbnailRendition(pictures[i]);
            if (thumbnail != null && thumbnail.href != null) {
                return {item: pictures[i], href: thumbnail.href};
            }
        }
    }

    return undefined;
}

/**
 * Get picture preview rendition
 *
 * @param {Object} picture
 * @return {Object}
 */
export function getPreviewRendition(picture: any, isCustom: any = false) {
    return get(
        picture,
        isCustom ? 'renditions._newsroom_custom' : 'renditions._newsroom_base',
        get(picture, 'renditions.viewImage')
    );
}

/**
 * Get picture detail rendition
 *
 * @param {Object} picture
 * @return {Object}
 */
export function getDetailRendition(picture: any, isCustom: any = false) {
    return get(
        picture,
        isCustom ? 'renditions._newsroom_custom' : 'renditions._newsroom_base',
        get(picture, 'renditions.baseImage')
    );
}

/**
 * Get picture detail rendition
 *
 * @param {Object} picture
 * @return {Object}
 */
export function isCustomRendition(picture: any) {
    return !!get(picture, 'renditions._newsroom_custom');
}

/**
 * Get original video
 *
 * @param {Object} video
 * @return {Object}
 */
export function getOriginalRendition(video: any) {
    return get(video, 'renditions.original');
}

/**
 * Test if an item is killed
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function isKilled(item: any) {
    return item.pubstatus === STATUS_KILLED;
}

/**
 * Checks if item is preformatted
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function isPreformatted(item: any) {
    return (item.body_html || '').includes('<pre>');
}

/**
 * Test if other item versions should be visible
 *
 * @param {Object} item
 * @param {bool} next toggle if checking for next or previous versions
 * @return {Boolean}
 */
export function showItemVersions(item: any, next?: any) {
    return !isKilled(item) && (next || item.ancestors && item.ancestors.length);
}

/**
 * Get short text for lists
 *
 * @param {Item} item
 * @return {Node}
 */
export function shortText(item: any, length: any = 40, config?: any) {
    const useBody = (config === true || config === false) ? config : isDisplayed('abstract', config) === false;
    const html = (useBody ? item.body_html : item.description_html || item.body_html) || '<p></p>';
    const text = useBody ?  getTextFromHtml(html) : item.description_text || getTextFromHtml(html);
    const words = text.split(/\s/).filter((w: any) => w);
    return words.slice(0, length).join(' ') + (words.length > length ? '...' : '');
}

/**
 * Split text into an array of words
 *
 * @todo: Any changes to this code **must** be reflected in the python version as well
 * @see superdesk-client-core:scripts/core/count-words.ts:countWords
 * @see newsroom.utils.split_words
 */
function splitWords(str: string): Array<string> {
    const strTrimmed = str.trim();

    if (strTrimmed.length < 1) {
        return [];
    }

    return strTrimmed
        .replace(/\n/g, ' ') // replace newlines with spaces

        // Remove spaces between two numbers
        // 1 000 000 000 -> 1000000000
        .replace(/([0-9]) ([0-9])/g, '$1$2')

        // remove anything that is not a unicode letter, a space, comma or a number
        .replace(/[^\p{L} 0-9,]/gu, '')

        // replace two or more spaces with one space
        .replace(/ {2,}/g, ' ')

        .trim()
        .split(' ');
}

/**
 * Extract text from a node, handling both text and element nodes.
 *
 * @param {Node | null} node - The node from which to extract text.
 * @returns {string} - The extracted text from the node.
 */
function getTextFromNode(node: Node | null): string {
    if (!node) return '';
    if (node.nodeType === Node.TEXT_NODE) {
        const textContent = node.textContent || '';
        return textContent.trim();
    }
    return '';
}

/**
 * Returns first paragraph with highlighted text, and truncates output to ``max_length`` words
 *
 * @todo Any changes to this code **must** be reflected in the python version as well
 * @see newsroom.utils.short_highlighted_text
 *
 * @param {string} html - Original text
 * @param {number} maxLength - Maximum number of words
 * @returns {string}
 */
export function shortHighlightedtext(html: string, maxLength = 40) {
    const div = document.createElement('div');
    div.innerHTML = html;
    const highlightSpans = Array.from(div.querySelectorAll('span.es-highlight'));
    const extractedText: string[] = [];
    let lastNode: Node | null = null;

    for (const highlightSpan of highlightSpans) {
        const textBefore = lastNode === highlightSpan.previousSibling ? '' : getTextFromNode(highlightSpan.previousSibling);
        const textAfter = getTextFromNode(highlightSpan.nextSibling);

        if (textBefore) {
            extractedText.push(textBefore);
        }

        extractedText.push(highlightSpan.outerHTML);

        if (textAfter) {
            extractedText.push(textAfter);
        }

        lastNode = highlightSpan.nextSibling;
    }
    return extractedText.join(' ')+(html.length > maxLength ? '...' : ' ');
}

/**
 * Get caption for picture
 *
 * @param {Object} picture
 * @return {String}
 */
export function getCaption(picture: any) {
    return getTextFromHtml(picture.description_text || picture.body_text || '').trim();
}

export function getActiveQuery(query: any, activeFilter: any, createdFilter: any) {
    const queryParams: any = {
        query: query || null,
        filter: pickBy(activeFilter),
        created: pickBy(createdFilter),
    };

    return pickBy(queryParams, (val) => !isEmpty(val));
}

export function isTopicActive(topic: any, activeQuery: any) {
    const topicQuery = getActiveQuery(topic.query, topic.filter, topic.created);
    return !isEmpty(activeQuery) && isEqual(topicQuery, activeQuery);
}

/**
 * Test if 2 items are equal
 *
 * @param {Object} a
 * @param {Object} b
 * @return {Boolean}
 */
export function isEqualItem(a: any, b: any) {
    return a && b && a._id === b._id && a.version === b.version;
}

function hasMedia(item: any, type: any) {
    return item != null && getItemMedia(item).some((_item: any) => _item.type === type);
}

export function getContentTypes(item: IArticle): Set<IContentType> {
    const contentTypes = new Set<IContentType>();

    contentTypes.add(item.type);
    Object.values(item.associations ?? {})
        .forEach((item) => {
            if (item != null) {
                contentTypes.add(item.type);
            }
        });

    return contentTypes;
}

export const hasAudio = (item: any) => hasMedia(item, 'audio');
export const hasVideo = (item: any) => hasMedia(item, 'video');
