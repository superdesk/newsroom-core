import {gettext, isActionEnabled} from './utils';

export function getItemActions(dispatch: any, actions: any) {
    const {
        openItem,
        shareItems,
        printItem,
        previewAndCopy,
        downloadItems,
        bookmarkItems,
        removeBookmarks,
        removeItems,
    } = actions;

    return [
        {
            id: 'open',
            name: gettext('Open'),
            icon: 'text',
            when: (state: any) => !state.itemToOpen && !state.openItem,
            action: (item: any, group: any, plan: any) => dispatch(openItem(item, group, plan)),
        },
        {
            id: 'share',
            name: gettext('Share'),
            icon: 'share',
            multi: true,
            shortcut: true,
            visited: (user: any, item: any) => user && item && item.shares &&  item.shares.includes(user),
            when: (state: any) => state.user && state.company,
            action: (items: any) => dispatch(shareItems(items)),
        },
        {
            id: 'print',
            name: gettext('Print'),
            icon: 'print',
            visited: (user: any, item: any) => user && item && item.prints &&  item.prints.includes(user),
            action: (item: any) => dispatch(printItem(item)),
        },
        {
            id: 'copy',
            name: gettext('Copy'),
            icon: 'copy',
            visited: (user: any, item: any) => user && item && item.copies &&  item.copies.includes(user),
            action: (item: any) => dispatch(previewAndCopy(item)),
        },
        {
            id: 'download',
            name: gettext('Download'),
            icon: 'download',
            multi: true,
            visited: (user: any, item: any) => user && item && item.downloads &&  item.downloads.includes(user),
            when: (state: any) => state.user && (state.company || state.userType === 'administrator'),
            action: (items: any) => dispatch(downloadItems(items)),
        },
        {
            id: 'save',
            name: gettext('Save'),
            icon: 'bookmark-add',
            multi: true,
            shortcut: true,
            when: (state: any, item: any) => state.user && (!item || !item.bookmarks ||  !item.bookmarks.includes(state.user)),
            action: (items: any) => dispatch(bookmarkItems(items)),
        },
        {
            id: 'unsave',
            name: gettext('Unsave'),
            icon: 'bookmark-remove',
            multi: true,
            shortcut: true,
            when: (state: any, item: any) => state.user && item && item.bookmarks && item.bookmarks.includes(state.user),
            action: (items: any) => dispatch(removeBookmarks(items)),
        },
        {
            id: 'remove',
            name: gettext('Remove'),
            icon: 'trash',
            multi: true,
            when: (state: any) => state.user && state.userType === 'administrator',
            action: (items: any) => removeItems(items),
        }
    ].filter(isActionEnabled('item_actions'));
}
