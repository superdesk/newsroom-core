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
export function getIntVersion(item) {
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
export function getVideos(item) {
    return getRelatedItemsByType(item, 'video');
}

const isMedia = (item) => item.type === 'audio' || item.type === 'video';

/**
 * 
 * @param {*} item 
 */
export function getItemMedia(item) {
    if (isMedia(item)) {
        return [item];
    }

    return Object.values(get(item, 'associations', {}) || {}).filter((assoc) => assoc != null && isMedia(assoc));
}

function getRelatedItemsByType(item, type) {
    return item.type === type ? [item] : Object.values(get(item, 'associations', {}) || {}).filter((assoc) => get(assoc, 'type') === type);
}

export function getFeatureMedia(item) {
    if (['picture', 'video', 'audio'].includes(item.type)) {
        return item;
    }

    const featured = get(item, 'associations.featuremedia');

    if (featured != null && ['picture', 'video', 'audio'].includes(featured.type)) {
        return featured;
    }

    return getBodyPicture(item);
}

export function getOtherMedia(item) {
    if (['picture', 'video', 'audio'].includes(item.type)) {
        return null;
    }

    return Object.keys(item.associations || {})
        .filter((key) => (
            !key.startsWith('editor_') &&
            key !== 'featuremedia' &&
            item.associations[key] != null &&
            ['video', 'audio'].includes(item.associations[key].type)
        ))
        .map((key) => item.associations[key]);
}

/**
 * Get picture for an item
 *
 * if item is picture return it, otherwise look for featuremedia
 *
 * @param {Object} item
 * @return {Object}
 */
export function getPicture(item) {
    if (item.type === 'picture') {
        return item;
    }

    const featured = get(item, 'associations.featuremedia');

    if (featured != null && featured.type === 'picture') {
        return featured;
    }

    return getBodyPicture(item);
}

function getBodyPicture(item) {
    const pictures = Object.values(get(item, 'associations', {}) || {}).filter((assoc) => get(assoc, 'type') === 'picture');
    return pictures.length ? pictures[0] : null;
}

export function getPictureList(item) {
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
export function getThumbnailRendition(picture, large) {
    const rendition = large ? 'renditions._newsroom_thumbnail_large' : 'renditions._newsroom_thumbnail';
    return get(picture, rendition, get(picture, 'renditions.thumbnail'));
}

export function getImageForList(item) {
    const pictures = getPictureList(item);
    let thumbnail;

    for (let i = 0; i < pictures.length; i++) {
        thumbnail = getThumbnailRendition(pictures[i]);

        if (thumbnail != null && thumbnail.href != null) {
            return {item: pictures[i], href: thumbnail.href};
        }
    }

    return null;
}

/**
 * Get picture preview rendition
 *
 * @param {Object} picture
 * @return {Object}
 */
export function getPreviewRendition(picture, isCustom = false) {
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
export function getDetailRendition(picture, isCustom = false) {
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
export function isCustomRendition(picture) {
    return !!get(picture, 'renditions._newsroom_custom');
}

/**
 * Get original video
 *
 * @param {Object} video
 * @return {Object}
 */
export function getOriginalRendition(video) {
    return get(video, 'renditions.original');
}

/**
 * Test if an item is killed
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function isKilled(item) {
    return item.pubstatus === STATUS_KILLED;
}

/**
 * Checks if item is preformatted
 *
 * @param {Object} item
 * @return {Boolean}
 */
export function isPreformatted(item) {
    return (item.body_html || '').includes('<pre>');
}

/**
 * Test if other item versions should be visible
 *
 * @param {Object} item
 * @param {bool} next toggle if checking for next or previous versions
 * @return {Boolean}
 */
export function showItemVersions(item, next) {
    return !isKilled(item) && (next || item.ancestors && item.ancestors.length);
}

/**
 * Get short text for lists
 *
 * @param {Item} item
 * @return {Node}
 */
export function shortText(item, length=40, config) {
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
export function getCaption(picture) {
    return getTextFromHtml(picture.description_text || picture.body_text || '').trim();
}

export function getActiveQuery(query, activeFilter, createdFilter) {
    const queryParams = {
        query: query || null,
        filter: pickBy(activeFilter),
        created: pickBy(createdFilter),
    };

    return pickBy(queryParams, (val) => !isEmpty(val));
}

export function isTopicActive(topic, activeQuery) {
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
export function isEqualItem(a, b) {
    return a && b && a._id === b._id && a.version === b.version;
}

function hasMedia(item, type) {
    return item != null && getItemMedia(item).some((_item) => _item.type === type);
}

export function getContentTypes(item) {
    const contentTypes = new Set();

    contentTypes.add(item.type);
    Object.values(item.associations || {})
        .map((association) => association.type)
        .forEach((mediaType) => {
            contentTypes.add(mediaType);
        });

    return contentTypes;
}

export const hasAudio = (item) => hasMedia(item, 'audio');
export const hasVideo = (item) => hasMedia(item, 'video');