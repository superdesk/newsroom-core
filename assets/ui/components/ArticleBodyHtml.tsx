import React from 'react';
import {memoize} from 'lodash';
import {formatHTML} from 'utils';
import {connect} from 'react-redux';
import {selectCopy} from '../../wire/actions';
import {IArticle} from 'interfaces';
import {extensions} from 'index';

function isLinkExternal(href: string) {
    try {
        const url = new URL(href);

        // Check if the hosts are different and protocol is http or https
        return url.host !== window.location.host && ['http:', 'https:'].includes(url.protocol);
    } catch (e) {
        // will throw if string is not a valid link
        return false;
    }
}

interface IOwnProps {
    item: IArticle;
}

interface IMapDispatchToProps {
    reportCopy(item: IArticle): void;
}

interface IState {
    error: boolean;
}

type IProps = IOwnProps & IMapDispatchToProps;

const getBodyElement = memoize<(html: string, item: IArticle) => HTMLElement>(_getBodyElement);

class ArticleBodyHtmlComponent extends React.PureComponent<IProps, IState> {
    private bodyRef: React.RefObject<HTMLDivElement>;

    constructor(props: any) {
        super(props);
        this.copyClicked = this.copyClicked.bind(this);
        this.clickClicked = this.clickClicked.bind(this);

        this.bodyRef = React.createRef<HTMLDivElement>();
        this.state = {error: false};
    }

    componentDidMount() {
        if (this.renderPreview()) {
            document.addEventListener('copy', this.copyClicked);
            document.addEventListener('click', this.clickClicked);
        }
    }

    componentWillUnmount() {
        document.removeEventListener('copy', this.copyClicked);
        document.removeEventListener('click', this.clickClicked);
    }

    static getDerivedStateFromError(error: any): IState {
        console.error('HTML Error', error);
        return {error: true};
    }

    private clickClicked(event: any) {
        if (event != null) {
            const target = event.target;

            if (target && target.tagName === 'A' && isLinkExternal(target.href)) {
                event.preventDefault();
                event.stopPropagation();

                // security https://mathiasbynens.github.io/rel-noopener/
                const nextWindow: any = window.open();

                nextWindow.opener = null;
                nextWindow.location.href = target.href;
            }
        }
    }

    private copyClicked() {
        this.props.reportCopy(this.props.item);
    }

    private renderPreview() : boolean {
        const item = this.props.item;
        const bodyHtml = (item.es_highlight?.body_html ?? '').length > 0 ?
            item.es_highlight?.body_html[0] :
            item.body_html;
        
        if (this.bodyRef.current == null) {
            return false;
        }

        if (bodyHtml == null) {
            this.bodyRef.current.innerHTML = '';
            return false;
        }

        const body = getBodyElement(bodyHtml, item);

        this.bodyRef.current.innerHTML = body.innerHTML;

        return true;
    }

    render() {
        if (this.state.error) {
            return <div className='wire-column__preview__text wire-column__preview__text--pre'>{'...'}</div>;
        }

        return (
            <div
                id='preview-body'
                ref={this.bodyRef}
                className='wire-column__preview__text wire-column__preview__text--pre'
            />
        );
    }
}

const mapDispatchToProps = (dispatch: any) => ({
    reportCopy: (item: any) => dispatch(selectCopy(item))
});

export const ArticleBodyHtml = connect<{}, IMapDispatchToProps, IOwnProps>(null, mapDispatchToProps)(ArticleBodyHtmlComponent);

/**
 * Update Image Embeds to use the Web APIs Assets endpoint
 *
 * @param html - The `body_html` value (could also be the ES Highlight version)
 * @returns {string}
 * @private
 */
function _updateImageEmbedSources(html: string, item: IArticle): HTMLElement {
    const associations: NonNullable<IArticle['associations']> = item.associations ?? {};

    // Get the list of Original Rendition IDs for all Image Associations
    const imageEmbedOriginalIds = Object
        .keys(associations)
        .filter((key: any) => key.startsWith('editor_'))
        .map((key: any) => associations[key]?.renditions?.['original']?.media)
        .filter((value: any) => value != null);

    const container = new DOMParser().parseFromString(html, 'text/html');

    if (!imageEmbedOriginalIds.length) {
        // This item has no Image Embeds
        // return the supplied html as-is
        return container.body;
    }

    // Create a DOM node tree from the supplied html
    // We can then efficiently find and update the image sources
    let imageSourcesUpdated = false;

    container
        .querySelectorAll('img, video, audio')
        .forEach((mediaTag: any) => {
            // Using the tag's `src` attribute, find the Original Rendition's ID
            const originalMediaId = imageEmbedOriginalIds.find((mediaId: any) => (
                !mediaTag.src.startsWith('/assets/') &&
                mediaTag.src.includes(mediaId))
            );

            if (mediaTag instanceof HTMLVideoElement) {
                mediaTag.preload = 'metadata';
            }

            if (originalMediaId) {
                // We now have the Original Rendition's ID
                // Use that to update the `src` attribute to use Newshub's Web API
                imageSourcesUpdated = true;
                mediaTag.src = `/assets/${originalMediaId}`;
            }
        });

    return container.body;
}

function _getBodyElement(bodyHtml: string, item: IArticle): HTMLElement {
    const output = _updateImageEmbedSources(formatHTML(bodyHtml), item);
    const prepareWirePreview = extensions.prepareWirePreview ?? ((element) => element);
    return prepareWirePreview(
        output,
        item,
    );
}
