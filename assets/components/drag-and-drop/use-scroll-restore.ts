import React, {useState, useRef, useEffect, createRef} from 'react';
import {getScrollableAncestors} from '@dnd-kit/core';

export function useScrollRestore(ref: React.RefObject<HTMLDivElement>) {
    const scrollableParent = useRef<Element>();
    const lastScrollPosition = useRef<number | null>(0); // of scrollable parent

    useEffect(() => {
        scrollableParent.current = getScrollableAncestors(ref.current)[0];
    }, []);

    return {
        savePosition: () => {
            lastScrollPosition.current = scrollableParent.current?.scrollTop ?? null;
        },
        restoreSavedPosition: () => {
            setTimeout(() => {
                /**
                 * Restore last scroll position in case auto-scrolling was performed while dragging.
                 * Without this, after scrolling and dropping, scroll jumps to position as if no scrolling happened.
                 * I suspect it might be because `moveTopic` is async, the dragging library might assume that dropping was cancelled.
                 */
                if (scrollableParent.current != null && lastScrollPosition.current != null) {
                    scrollableParent.current.scrollTop = lastScrollPosition.current;
                } else {
                    // reset last scroll position
                    lastScrollPosition.current = scrollableParent.current?.scrollTop ?? null;
                }
            });
        },
    };
}

