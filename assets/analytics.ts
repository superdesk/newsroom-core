import {get} from 'lodash';

class Analytics {
    _event(name, params) {
        if (window.gtag) {
            const company = get(window, 'profileData.companyName', 'none');
            const user = get(window, 'profileData.user.first_name', 'unknown');
            const userParams = {
                event_category: company,
                company: company,
                user: user,
            };

            window.gtag('event', name, Object.assign(userParams, params));
        }
    }

    event(name: any, label: any, params: any) {
        this._event(name, Object.assign({
            event_label: label,
        }, params));
    }

    itemEvent(name: any, item: any, params: any) {
        this.event(name, item.headline || item.name || item.slugline, params);
    }

    timingComplete(name: any, value: any) {
        this._event('timing_complete', {name, value});
    }

    pageview(title: any, path: any) {
        this._event('page_view', {
            page_title: title,
            page_path: path,
        });
    }

    itemView(item) {
        if (item) {
            this.pageview(item.headline || item.slugline, `/${item._type}/${item._id}`);
        } else {
            this.pageview();
        }
    }

    sendEvents(events: any) {
        events.forEach((event) => {
            this._event(event);
        });
    }

    multiItemEvent(event: any, items: any) {
        items.forEach((item) => item && this.itemEvent(event, item));
    }
}

// make it available
window.analytics = new Analytics();
export default window.analytics;