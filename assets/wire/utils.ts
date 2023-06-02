import {get, isEmpty, isEqual, pickBy} from 'lodash';
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

const isMedia = (item) => item.type === 'audio' || item.type === 'video';

/**
 * 
 * @param {*} item 
 */
export function getItemMedia(item: any) {
    if (isMedia(item)) {
        return [item];
    }

    return Object.values(get(item, 'associations', {}) || {}).filter((assoc) => assoc != null && isMedia(assoc));
}

function getRelatedItemsByType(item: any, type: any) {
    return item.type === type ? [item] : Object.values(get(item, 'associations', {}) || {}).filter((assoc) => get(assoc, 'type') === type);
}

/**
 * Get picture for an item
 *
 * if item is picture return it, otherwise look for featuremedia
 *
 * @param {Object} item
 * @return {Object}
 */
export function getPicture(item: any) {
    if (item.type === 'picture') {
        return item;
    }

    const featured = get(item, 'associations.featuremedia');

    if (featured != null && featured.type === 'picture') {
        return featured;
    }

    return getBodyPicture(item);
}

function getBodyPicture(item: any) {
    const pictures = Object.values(get(item, 'associations', {}) || {}).filter((assoc) => get(assoc, 'type') === 'picture');
    return pictures.length ? pictures[0] : null;
}

export function getPictureList(item: any) {
    const pictures = Object.values(get(item, 'associations', {}) || {}).filter((assoc) => get(assoc, 'type') === 'picture');
    return pictures.length ? pictures : [];
}

/**
 * Get picture thumbnail rendition specs
 *
 * @param {Object} picture
 * @param {Boolean} large
 * @return {Object}
 */
export function getThumbnailRendition(picture: any, large: any) {
    const rendition = large ? 'renditions._newsroom_thumbnail_large' : 'renditions._newsroom_thumbnail';
    return get(picture, rendition, get(picture, 'renditions.thumbnail'));
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
export function showItemVersions(item: any, next: any) {
    return !isKilled(item) && (next || item.ancestors && item.ancestors.length);
}

/**
 * Get short text for lists
 *
 * @param {Item} item
 * @return {Node}
 */
export function shortText(item: any, length: any = 40, config: any) {
    const useBody = (config === true || config === false) ? config : isDisplayed('abstract', config) === false;
    const html = (useBody ? item.body_html : item.description_html || item.body_html) || '<p></p>';
    const text = useBody ?  getTextFromHtml(html) : item.description_text || getTextFromHtml(html);
    const words = text.split(/\s/).filter((w) => w);
    return words.slice(0, length).join(' ') + (words.length > length ? '...' : '');
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
    const queryParams = {
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
    return item != null && getItemMedia(item).some((_item) => _item.type === type);
}

export const hasAudio = (item) => hasMedia(item, 'audio');
export const hasVideo = (item) => hasMedia(item, 'video');