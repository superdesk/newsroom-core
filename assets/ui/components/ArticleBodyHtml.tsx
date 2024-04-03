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

type IProps = IOwnProps & IMapDispatchToProps;

class ArticleBodyHtmlComponent extends React.PureComponent<IProps> {
    private getBodyHTML: any;
    private bodyRef: React.RefObject<HTMLDivElement>;

    constructor(props: any) {
        super(props);
        this.copyClicked = this.copyClicked.bind(this);
        this.clickClicked = this.clickClicked.bind(this);

        // use memoize so this function is only called when `body_html` changes
        this.getBodyHTML = memoize(this._getBodyHTML.bind(this));

        this.bodyRef = React.createRef<HTMLDivElement>();
    }


    componentDidMount() {
        const item = this.props.item;
        const html = this.getBodyHTML(
            (item.es_highlight?.body_html ?? '').length > 0 ?
                item.es_highlight?.body_html[0] :
                item.body_html
        );

        if (!html) {
            return;
        }

        const prepareWirePreview = extensions.prepareWirePreview ?? ((element) => element);
        const previewElement = prepareWirePreview(new DOMParser().parseFromString(html, 'text/html').body);

        if (this.bodyRef.current == null) {
            return;
        }

        this.bodyRef.current.appendChild(previewElement);

        this.loadIframely(); // https://iframely.com/docs/react
        this.executeScripts();
        document.addEventListener('copy', this.copyClicked);
        document.addEventListener('click', this.clickClicked);

    }

    componentWillUnmount() {
        document.removeEventListener('copy', this.copyClicked);
        document.removeEventListener('click', this.clickClicked);
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

    private loadIframely() {
        const html = this.props.item?.body_html ?? '';

        if (window.iframely && html && html.includes('iframely')) {
            window.iframely.load();
        }
    }

    private executeScripts() {
        const tree: any = this.bodyRef.current;
        const loaded: Array<any> = [];

        if (tree == null) {
            return;
        }

        tree.querySelectorAll('script').forEach((s: any) => {
            if (s.hasAttribute('src') && !loaded.includes(s.getAttribute('src'))) {
                let url = s.getAttribute('src');

                loaded.push(url);

                if (url.includes('twitter.com/') && window.twttr != null) {
                    window.twttr.widgets.load();
                    return;
                }

                if (url.includes('instagram.com/') && window.instgrm != null) {
                    window.instgrm.Embeds.process();
                    return;
                }

                if (url.startsWith('http')) {
                    // change https?:// to // so it uses schema of the client
                    url = url.substring(url.indexOf(':') + 1);
                }

                const script: any = document.createElement('script');

                script.src = url;
                script.async = true;

                script.onload = () => {
                    document.body.removeChild(script);
                };

                script.onerrror = (error: any) => {
                    throw new URIError('The script ' + error.target.src + 'didn\'t load.');
                };

                document.body.appendChild(script);
            }
        });
    }

    private copyClicked() {
        this.props.reportCopy(this.props.item);
    }

    private _getBodyHTML(bodyHtml: any) {
        return !bodyHtml ?
            null :
            this._updateImageEmbedSources(formatHTML(bodyHtml));
    }

    /**
     * Update Image Embeds to use the Web APIs Assets endpoint
     *
     * @param html - The `body_html` value (could also be the ES Highlight version)
     * @returns {string}
     * @private
     */
    private _updateImageEmbedSources(html: any) {
        const item = this.props.item;

        const associations: NonNullable<IArticle['associations']> = item.associations ?? {};

        // Get the list of Original Rendition IDs for all Image Associations
        const imageEmbedOriginalIds = Object
            .keys(associations)
            .filter((key: any) => key.startsWith('editor_'))
            .map((key: any) => associations[key]?.renditions?.['original']?.media)
            .filter((value: any) => value != null);

        if (!imageEmbedOriginalIds.length) {
            // This item has no Image Embeds
            // return the supplied html as-is
            return html;
        }

        // Create a DOM node tree from the supplied html
        // We can then efficiently find and update the image sources
        const container = document.createElement('div');
        let imageSourcesUpdated = false;

        container.innerHTML = html;
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

        // If Image tags were not updated, then return the supplied html as-is
        return imageSourcesUpdated ? container.innerHTML : html;
    }

    render() {
        // preview element will be populated in `componentDidMount`

        return (
            <div
                ref={this.bodyRef}
                className='wire-column__preview__text wire-column__preview__text--pre'
                id='preview-body'
            />
        );
    }
}

const mapDispatchToProps = (dispatch: any) => ({
    reportCopy: (item: any) => dispatch(selectCopy(item))
});

const ArticleBodyHtmlConnected: React.ComponentType<IProps> = connect(null, mapDispatchToProps)(ArticleBodyHtmlComponent);

// component needs to reinitialize if item changes
export const ArticleBodyHtml: React.ComponentType<IProps> = (props) => <ArticleBodyHtmlConnected {...props} key={props.item._id} />;
